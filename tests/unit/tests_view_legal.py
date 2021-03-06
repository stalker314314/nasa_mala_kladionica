# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class LegalTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.about))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse(views.terms))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse(views.privacy))
        self.assertEqual(response.status_code, 200)

    def test_regular_user(self):
        """
        Test all static legal view
        """
        response = self.client.get(reverse(views.about))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse(views.terms))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse(views.privacy))
        self.assertEqual(response.status_code, 200)
