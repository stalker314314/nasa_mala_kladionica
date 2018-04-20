# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase, Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models


class ResultsTests(TestCase):
    fixtures = ['initial_data.json']

    def test_anon_user(self):
        """
        Test result view with anonymous user
        """
        self.client = Client()
        response = self.client.get(reverse(views.results))
        self.assertEqual(response.status_code, 302)

    def test_no_active_round(self):
        """
        Test result view with logged user
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        response = self.client.get(reverse(views.results))
        self.assertEqual(response.status_code, 200)