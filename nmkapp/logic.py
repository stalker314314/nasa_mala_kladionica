from nmkapp.models import Player, UserRound, Shot


def recalculate_total_points():
    players = Player.objects.select_related('user').all()
    user_rounds = UserRound.objects.select_related('user').all()
    for player in players:
        player.points = 0.0
        for user_round in user_rounds:
            if player.user == user_round.user:
                player.points += user_round.points
        player.points = round(player.points, 2)
        player.save()


def recalculate_round_points(this_round, recalculate_total=True):
    user_rounds = UserRound.objects.filter(round=this_round)
    shots = Shot.objects.select_related('user_round', 'match').filter(user_round__round=this_round)
    for user_round in user_rounds:
        user_round.points = 0.0
        for shot in shots:
            if shot.user_round == user_round and shot.match.result is not None and shot.shot == shot.match.result:
                if shot.match.result == 1:
                    user_round.points += shot.match.odd1
                elif shot.match.result == 0:
                    user_round.points += shot.match.oddX
                else:
                    user_round.points += shot.match.odd2
        user_round.points = round(user_round.points, 2)
        user_round.save()
    if recalculate_total:
        recalculate_total_points()
