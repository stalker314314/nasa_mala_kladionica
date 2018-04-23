# -*- coding: utf-8 -*-

from nmkapp import send_shots_cron

from ..nmk_unit_test_case import NmkUnitTestCase


class SendShotsCronTests(NmkUnitTestCase):
    def test_no_round_started(self):
        rounds = send_shots_cron.main()
        self.assertEqual(len(rounds), 0)
