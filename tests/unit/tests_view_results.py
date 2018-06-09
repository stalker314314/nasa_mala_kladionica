# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views
from .nmk_unit_test_case import NmkUnitTestCase


class ResultsTests(NmkUnitTestCase):
    def test_anon_user(self):
        """
        Test result view with anonymous user
        """
        self.client = Client()
        response = self.client.get(reverse(views.results))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        """
        Test result view with logged user
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan@mail.com', password='12345'))
        response = self.client.get(reverse(views.results))
        self.assertEqual(response.status_code, 200)
