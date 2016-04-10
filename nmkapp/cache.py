import hashlib

from django.core.cache import cache

from nmkapp.models import Player, Round, Shot, UserRound

class StandingsCache():
    def __init__(self, group = None):
        self.group = group
        
    def get_key(self):
        group_key = hashlib.sha256((self.group.name + 'v3').encode('utf-8')).hexdigest() if self.group is not None else 'v3'
        return "standings/%s" % group_key
        
    def clear(self):
        cache.delete(self.get_key())

    def get(self, rounds):
        standings = []
        group_key = self.get_key()
        standings_from_cache = cache.get(group_key)
        if standings_from_cache is None:
            user_rounds = list(UserRound.objects.select_related('user', 'round').all())
            players = Player.objects.select_related('user').all()
            # create a matrix of [users][rounds] = points
            players_count = len(players)
            rounds_count = len(rounds)
            player_matrix_mapping = {}
            rounds_matrix_mapping = {}
            ur_matrix = [[0 for x in range(rounds_count)] for x in range(players_count)]
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
                standing = [ player, round_standings, player.points ]
                standings.append(standing)
            standings = sorted(standings, key=lambda s: (-s[2], s[0].user.first_name, s[0].user.last_name))
            # populate positions
            position = 1
            position_increment = 1
            previous_points = None
            for standing in standings:
                if previous_points != None:
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

class UserRoundShotCache:
    def __init__(self, user_round):
        self.user_round = user_round
    
    def get_key(self):
        return "shots_by_user_round/%d" % self.user_round.id
    
    def clear(self):
        cache.delete(self.get_key())

    def get(self):
        shots_from_cache = cache.get(self.get_key())
        if shots_from_cache is None:
            shots = Shot.objects.select_related('match', 'match__home_team', 'match__away_team').filter(user_round=self.user_round).order_by("match__start_time", "match")
            cache.add(self.get_key(), shots)
        else:
            shots = list(shots_from_cache)
        
        return shots