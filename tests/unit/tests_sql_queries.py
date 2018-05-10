# -*- coding: utf-8 -*-

from django.test import TransactionTestCase
from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class IssuedQuerriesTests(NmkUnitTestCase):

    def test_test(self):
        with self.assertNumQueriesLessThan(120):
            self.client = Client()
            self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))

            response = self.client.get(reverse(views.home))
            self.assertEqual(response.status_code, 200)
