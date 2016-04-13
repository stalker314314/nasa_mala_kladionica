from nmkapp.models import Round, UserRound, Shot, Match, Team, Player, Group

def player_stats(request):
    player_count = len(Player.objects.all())
    player_money_count = len(Player.objects.filter(in_money = True))
    reward_money1 = (9.0 * player_money_count) / 2
    reward_money2 = 3 * player_money_count
    reward_money3 = (9.0 * player_money_count)/6
    reward_money = {'1': reward_money1, '2': reward_money2, '3': reward_money3 }
    return {'ctx_stats': {
                          'player_count': player_count,
                          'player_money_count': player_money_count,
                          'reward_money': reward_money
                          }
            }