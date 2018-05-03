# -*- coding: utf-8 -*-

import datetime

from django.core import mail

from nmkapp import send_reminder_cron, models
from ..nmk_unit_test_case import NmkUnitTestCase


class SendReminderCronTests(NmkUnitTestCase):
    def test_no_reminders(self):
        """
        Tests that there is reminder when round is not starting in next 24h
        """
        with self.settings(SEND_MAIL=True):
            rounds = send_reminder_cron.main()
        self.assertEqual(len(rounds), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_send_reminder(self):
        """
        Test actually sending a reminder
        """
        # Setup so that round start in exactly 24h
        nmk_round = models.Round.objects.filter(name='Final')[0]
        nmk_round.active = True
        nmk_round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        match.save()

        player = models.Player.objects.filter(user__id=3).get()
        player.language = 'sr'
        player.save()

        with self.settings(SEND_MAIL=True):
            rounds = send_reminder_cron.main()
        self.assertEqual(len(rounds), 1)
        self.assertEqual(rounds[0][0].id, 3)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['gumi@mail.com', ])
        self.assertEqual(mail.outbox[0].subject, '[sharkz.bet] Round "Final" reminder')
        self.assertEqual(mail.outbox[1].to, ['seki@mail.com', ])
        self.assertEqual(mail.outbox[1].subject, '[sharkz.bet] Подсетник клађења на коло „Final“')

    def test_send_reminder_no_receivers(self):
        """
        Test that user don't receive mail when they turn off mail notifications
        """
        # Setup so that round start in exactly 24h
        nmk_round = models.Round.objects.filter(name='Final')[0]
        nmk_round.active = True
        nmk_round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        match.save()

        for player_id in [2, 3]:
            player = models.Player.objects.filter(user__id=player_id).get()
            player.send_mail_reminder = False
            player.save()

        with self.settings(SEND_MAIL=True):
            rounds = send_reminder_cron.main()
        self.assertEqual(len(rounds), 1)
        self.assertEqual(rounds[0][0].id, 3)
        self.assertEqual(len(mail.outbox), 0)
