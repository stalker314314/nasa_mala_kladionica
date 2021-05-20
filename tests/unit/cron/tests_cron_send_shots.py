# -*- coding: utf-8 -*-

import datetime

from django.core import mail

from nmkapp import send_shots_cron, models
from ..nmk_unit_test_case import NmkUnitTestCase


class SendShotsCronTests(NmkUnitTestCase):
    def test_no_round_started(self):
        with self.settings(SEND_MAIL=True):
            rounds = send_shots_cron.main()
        self.assertEqual(len(rounds), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_round_started(self):
        """
        Tests that mail get sent when round is actually just started
        """
        # Setup that round starts now
        nmk_round = models.Round.objects.filter(name='Final')[0]
        nmk_round.active = True
        nmk_round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now()
        match.save()

        # Setup that player 3 don't get mail, so we test that too
        player = models.Player.objects.filter(user__id=3).get()
        player.send_mail_round_started = False
        player.save()

        # Setup different language for player 2
        player = models.Player.objects.filter(user__id=2).get()
        player.language = 'sr'
        player.save()

        with self.settings(SEND_MAIL=True):
            rounds = send_shots_cron.main()
        self.assertEqual(len(rounds), 1)
        self.assertEqual(rounds[0].id, 3)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['kokan@mail.com', ])
        self.assertEqual(mail.outbox[0].subject, '[nmk.bet] Round "Final" started')
        self.assertEqual(mail.outbox[1].to, ['gumi@mail.com', ])
        self.assertEqual(mail.outbox[1].subject, '[nmk.bet] Почело коло „Final“')
