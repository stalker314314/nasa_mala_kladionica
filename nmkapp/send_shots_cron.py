#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cron job to send mail if first match from round is started.
"""

# ################### bootstrap django ##############################
import os
import sys
import datetime
import logging
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nmk.settings")
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../")

django.setup()
#####################################################################

from nmkapp.models import Round, Match, UserRound, Shot, Player

from django.template import loader
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import translation
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def get_rounds_just_started():
    current_time = datetime.datetime.now()
    previous_time = current_time - datetime.timedelta(minutes=15)
    
    all_rounds = Round.objects.all()
    rounds_to_return = []
    for nmk_round in all_rounds:
        matches1 = Match.objects.all().filter(round=nmk_round).filter(start_time__lte=current_time).count()
        matches2 = Match.objects.all().filter(round=nmk_round).filter(start_time__lte=previous_time).count()
        if (matches1 > 0) and (matches2 == 0):
            rounds_to_return.append(nmk_round)
    return rounds_to_return


def send_mail_for_round(nmk_round):
    matches = list(Match.objects.filter(round=nmk_round).order_by("start_time", "id"))
    round_standings = []
    
    user_rounds = UserRound.objects.filter(round=nmk_round).order_by("user__first_name", "user__last_name")
    for user_round in user_rounds:
        shots = list(Shot.objects.filter(user_round=user_round).order_by("match__start_time", "match"))
        round_standings.append({"user_round": user_round, "shots": shots})

    all_players = Player.objects.exclude(user__email='').filter(user__is_active=True).filter(send_mail=True)
    if settings.SEND_MAIL:
        logger.info("Sending mail that round %s started to %d players", nmk_round.name, len(all_players))
        for player in all_players:
            with translation.override(player.language):
                subject = _('[nmk] Round "%s" started') % nmk_round.name
                template = loader.get_template("mail/round_shots.html")
                message_text = template.render(
                    {"round": nmk_round, "matches": matches, "round_standings": round_standings})
            msg = EmailMessage(subject, message_text, "nmk@kokanovic.org", to=[player.user.email, ])
            msg.content_subtype = "html"
            msg.send(fail_silently=False)


def main():
    logger.info("Starting check to see if any round is started")
    rounds = get_rounds_just_started()
    logger.info("Started rounds %s", rounds)
    for nmk_round in rounds:
        send_mail_for_round(nmk_round)
    return rounds


if __name__ == '__main__':
    main()
