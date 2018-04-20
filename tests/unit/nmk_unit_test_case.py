# -*- coding: utf-8 -*-

from django.test import TestCase, Client


class NmkUnitTestCase(TestCase):
    fixtures = ['initial_data.json']

    def __init__(self, *args, **kwargs):
        super(NmkUnitTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))