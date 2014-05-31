#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cron job to send mail if first match from round is started.
"""

################# bootstrap django ##################################
import os
import sys
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nmk.settings")
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../")

from nmk import settings
#####################################################################

from nmkapp.models import Round, Match, UserRound, Shot, Player

from django.template import loader, Context
from django.conf import settings
from django.core.mail import EmailMessage

def get_rounds_just_started():
    current_time = datetime.datetime.now()
    previous_time = current_time - datetime.timedelta(minutes=15)
    
    rounds = Round.objects.all()
    rounds_to_return = []
    for round in rounds:
        matches1 = Match.objects.all().filter(round=round).filter(start_time__lte=current_time).count()
        matches2 = Match.objects.all().filter(round=round).filter(start_time__lte=previous_time).count()
        if (matches1 > 0) and (matches2 == 0):
            rounds_to_return.append(round)
    return rounds_to_return

def send_mail_for_round(round):
    matches = list(Match.objects.filter(round=round).order_by("start_time", "id"))
    round_standings = []
    
    user_rounds = UserRound.objects.filter(round=round).order_by("user__first_name", "user__last_name")
    for user_round in user_rounds:
        shots = list(Shot.objects.filter(user_round=user_round).order_by("match__start_time", "match"))
        round_standings.append({"user_round": user_round, "shots": shots})

    all_players = Player.objects.all()
    all_user_mail = [player.user.email for player in all_players if player.send_mail==True and player.user.email != ""]
    if len(all_user_mail) > 0:
        template = loader.get_template("mail/round_shots.html")
        message_text = template.render(Context({"round": round, "matches": matches, "round_standings": round_standings}))
        msg = EmailMessage(u"[nmk] Počelo kolo \"%s\"" % (round.name), message_text, "nmk-no-reply@nmk.kokanovic.org", bcc=all_user_mail)
        msg.content_subtype = "html"
        msg.send(fail_silently = False)

if __name__ == '__main__':
    if not settings.SEND_MAIL:
        return
    rounds = get_rounds_just_started()
    for round in rounds:
        send_mail_for_round(round)
