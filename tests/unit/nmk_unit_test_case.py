# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from nmkapp import logic

class NmkUnitTestCase(TestCase):
    fixtures = ['initial_data.json']

    def __init__(self, *args, **kwargs):
        super(NmkUnitTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        logic.recalculate_round_points(1)
        logic.recalculate_round_points(2)
        logic.recalculate_round_points(3)
        logic.recalculate_total_points()