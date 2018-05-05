# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class AboutTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.about))
        self.assertEqual(response.status_code, 200)

    def test_regular_user(self):
        """
        Test about view
        """
        response = self.client.get(reverse(views.about))
        self.assertEqual(response.status_code, 200)
