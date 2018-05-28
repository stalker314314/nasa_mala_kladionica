# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class LandingTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.landing))
        self.assertEqual(response.status_code, 200)

    def test_change_language(self):
        client = Client()
        # Check with other language set
        link_with_language = '{}?lang=sr'.format(reverse(views.landing))
        response = client.get(link_with_language)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Пријава' in response.content.decode('utf-8'))
        self.assertTrue('Anmelden' not in response.content.decode('utf-8'))

        # Check with another language
        link_with_language = '{}?lang=de'.format(reverse(views.landing))
        response = client.get(link_with_language)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Пријава' not in response.content.decode('utf-8'))
        self.assertTrue('Anmelden' in response.content.decode('utf-8'))

        # Check without language, but test is language is still set in session
        response = client.get(reverse(views.landing))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Пријава' not in response.content.decode('utf-8'))
        self.assertTrue('Anmelden' in response.content.decode('utf-8'))

    def test_regular_user(self):
        """
        Test visiting landing page
        """
        response = self.client.get(reverse(views.landing))
        self.assertEqual(response.status_code, 302)
