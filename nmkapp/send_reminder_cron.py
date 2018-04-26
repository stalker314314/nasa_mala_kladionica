#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cron job to send mail 24h before first game to users that didn't bet.
"""

# ################ bootstrap django #################################
import os
import sys
import datetime
import logging
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nmk.settings")
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../")

django.setup()
#####################################################################

from nmkapp.models import Round, Match, Shot, Player

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Min
from django.template import loader
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def get_rounds_starting_tomorrow():
    active_rounds = Round.objects.filter(active=True)
    rounds_to_return = []
    for nmk_round in active_rounds:
        min_time = Match.objects.filter(round=nmk_round).aggregate(Min('start_time'))['start_time__min']
        if min_time is None:
            continue            
        hours_diff = (min_time - datetime.datetime.now()).total_seconds() / (60 * 60)
        if 23.5 <= hours_diff < 24.5:
            rounds_to_return.append([nmk_round, min_time])
    return rounds_to_return


def send_reminder_for_round(nmk_round, min_time):
    all_players = Player.objects.exclude(user__email="").filter(send_mail=True).filter(user__is_active=True)
    player_mails = []
    for player in all_players:
        if not Shot.objects.filter(user_round__round=nmk_round).filter(user_round__user=player.user).exists():
            player_mails.append(player.user.email)
            
    template = loader.get_template("mail/round_reminder.html")
    message_text = template.render({"round": nmk_round, "min_time": min_time})
    if settings.SEND_MAIL:
        logger.info("Sending mail that round %s will be starting soon to %s", nmk_round.name, player_mails)
        for mail in player_mails:
            msg = EmailMessage(
                _('[nmk] Round "%s" reminder') % nmk_round.name, message_text, "nmk@kokanovic.org", to=[mail, ])
            msg.content_subtype = "html"
            msg.send(fail_silently=False)


def main():
    logger.info("Starting reminder check")
    rounds = get_rounds_starting_tomorrow()
    logger.info("Rounds starting in exactly next 24 hours: %s", rounds)
    for round_time in rounds:
        send_reminder_for_round(round_time[0], round_time[1])
    return rounds


if __name__ == '__main__':
    main()
