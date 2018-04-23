# -*- coding: utf-8 -*-

from nmkapp import send_reminder_cron

from ..nmk_unit_test_case import NmkUnitTestCase


class SendReminderCronTests(NmkUnitTestCase):
    def test_no_reminders(self):
        rounds = send_reminder_cron.main()
        self.assertEqual(len(rounds), 0)