import hashlib

from django.core.cache import cache

from nmkapp.models import Player, Round, Shot, UserRound, Group, Match

import logging
logger = logging.getLogger(__name__)


class StandingsCache:
    def __init__(self, group=None):
        self.group = group
        
    def get_key(self):
        group_key = hashlib.sha256((self.group.name + 'v3').encode('utf-8')).hexdigest()\
            if self.group is not None else 'v3'
        return "standings/%s" % group_key
        
    def clear(self):
        cache.delete(self.get_key())

    def get(self, rounds):
        standings = []
        group_key = self.get_key()
        standings_from_cache = cache.get(group_key)
        if standings_from_cache is None:
            user_rounds = list(UserRound.objects.select_related('user', 'user__player', 'round')
                               .filter(user__is_active=True))
            players = Player.objects.select_related('user').filter(user__is_active=True)
            # create a matrix of [users][rounds] = points
            players_count = len(players)
            rounds_count = len(rounds)
            player_matrix_mapping = {}
            rounds_matrix_mapping = {}
            ur_matrix = [[0 for _ in range(rounds_count)] for _ in range(players_count)]
            for user_round in user_rounds:
                if user_round.user.player.id not in player_matrix_mapping:
                    player_matrix_mapping[user_round.user.player.id] = players_count - 1
                    players_count = players_count - 1
                if user_round.round.id not in rounds_matrix_mapping:
                    rounds_matrix_mapping[user_round.round.id] = rounds_count - 1
                    rounds_count = rounds_count - 1
                ur_matrix[player_matrix_mapping[user_round.user.player.id]][rounds_matrix_mapping[user_round.round.id]] = user_round.points
            
            if self.group is not None:
                players = players.filter(groups__in=[self.group])
            for player in players:
                round_standings = []
                for this_round in rounds:
                    user_round = ur_matrix[player_matrix_mapping[player.id]][rounds_matrix_mapping[this_round.id]]
                    round_standings.append(user_round)
                standing = [player, round_standings, player.points]
                standings.append(standing)
            standings = sorted(standings, key=lambda s: (-s[2], s[0].user.first_name, s[0].user.last_name))
            # populate positions
            position = 1
            position_increment = 1
            previous_points = None
            for standing in standings:
                if previous_points is not None:
                    if previous_points != standing[2]:
                        position += position_increment
                        position_increment = 1
                    else:
                        position_increment += 1
                previous_points = standing[2]
                standing.append(position)
            cache.add(group_key, standings)
        else:
            standings = standings_from_cache
            
        return standings


class RoundStandingsCache:
    def __init__(self, nmk_round, group=None):
        self.round = nmk_round
        self.group = group

    def get_key(self):
        group_key = hashlib.sha256((self.group.name + 'v3').encode('utf-8')).hexdigest()\
            if self.group is not None else 'v3'
        return "round/%d/%s" % (self.round.id, group_key)

    def clear(self):
        cache.delete(self.get_key())

    @staticmethod
    def clear_round(nmk_round):
        groups = Group.objects.all()
        RoundStandingsCache(nmk_round).clear()
        for group in groups:
            RoundStandingsCache(nmk_round, group).clear()
        return groups

    @staticmethod
    def clear_group(group=None):
        rounds = Round.objects.all()
        for nmk_round in rounds:
            RoundStandingsCache(nmk_round, group).clear()
        return rounds

    @staticmethod
    def repopulate_round(nmk_round):
        groups = RoundStandingsCache.clear_round(nmk_round)
        for group in groups:
            RoundStandingsCache(nmk_round, group).get()

    @staticmethod
    def repopulate_group(group=None):
        rounds = RoundStandingsCache.clear_group(group)
        for nmk_round in rounds:
            RoundStandingsCache(nmk_round, group).get()

    def get(self):
        round_standings_from_cache = cache.get(self.get_key())
        if round_standings_from_cache is None:
            round_standings = []
            position = 1
            position_increment = 1

            shots = Shot.objects.\
                select_related('user_round', 'user_round__user', 'user_round__user__player', 'match',
                               'match__home_team', 'match__away_team').\
                filter(user_round__round=self.round).\
                filter(user_round__user__is_active=True)
            if self.group is not None:
                shots = shots.filter(user_round__user__player__groups__in=[self.group])
            shots = shots.order_by('-user_round__points', 'user_round__user__first_name', 'user_round__user__last_name',
                                   'match__start_time', 'match__id')
            
            last_user_round = None
            shots_in_user_round = []
            for shot in shots:
                if last_user_round is not None and last_user_round != shot.user_round:
                    ur_simple = {
                                 'username': last_user_round.user.username,
                                 'in_money': last_user_round.user.player.in_money,
                                 'full_name': '%s %s' % (last_user_round.user.first_name,
                                                         last_user_round.user.last_name),
                                 'points': last_user_round.points
                                 }
                    round_standings.append({'user_round': ur_simple, 'shots': shots_in_user_round,
                                            'position': position})
                    shots_in_user_round = []
                    if last_user_round.points != shot.user_round.points:
                        position += position_increment
                        position_increment = 1
                    else:
                        position_increment += 1
                last_user_round = shot.user_round
                shots_in_user_round.append({
                                            'shot': shot.shot,
                                            'match_result': shot.match.result
                                            })
            # Process last one
            if last_user_round is not None:
                ur_simple = {
                             'username': last_user_round.user.username,
                             'in_money': last_user_round.user.player.in_money,
                             'full_name': '%s %s' % (last_user_round.user.first_name, last_user_round.user.last_name),
                             'points': last_user_round.points
                             }
                round_standings.append({'user_round': ur_simple, 'shots': shots_in_user_round, 'position': position})
                position += 1
            # Add remaining users that didn't played shots in this round
            user_rounds_not_played = UserRound.objects.select_related('user', 'user__player').\
                filter(round=self.round).filter(shot=None).filter(user__is_active=True)
            if self.group is not None:
                user_rounds_not_played = user_rounds_not_played.filter(user__player__groups__in=[self.group])
            user_rounds_not_played = user_rounds_not_played.order_by('-points', 'user__first_name', 'user__last_name')
            if len(user_rounds_not_played) > 0:
                matches = Match.objects.filter(round=self.round).order_by('start_time', 'id')
                shots_in_user_round = []
                for match in matches:
                    shots_in_user_round.append({
                                                'shot': '',
                                                'match_result': match.result
                                                })
                for user_round_not_player in user_rounds_not_played:
                    ur_simple = {
                                 'username': user_round_not_player.user.username,
                                 'in_money': user_round_not_player.user.player.in_money,
                                 'full_name': '%s %s' % (user_round_not_player.user.first_name,
                                                         user_round_not_player.user.last_name),
                                 'points': user_round_not_player.points
                                 }
    
                    round_standings.append({'user_round': ur_simple, 'shots': shots_in_user_round,
                                            'position': position})
            cache.add(self.get_key(), round_standings)
        else:
            round_standings = round_standings_from_cache
        return round_standings
