# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class PaypalTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.paypal))
        self.assertEqual(response.status_code, 200)

    def test_regular_user(self):
        """
        Test visiting paypal page
        """
        player = models.Player.objects.filter(user__id=1)[0]
        self.assertFalse(player.in_money)

        response = self.client.get(reverse(views.paypal))
        self.assertEqual(response.status_code, 200)

        player = models.Player.objects.filter(user__id=1)[0]
        self.assertTrue(player.in_money)
