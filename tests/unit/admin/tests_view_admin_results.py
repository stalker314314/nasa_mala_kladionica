# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminResultsTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_results))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
        response = client.get(reverse(views.admin_results))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        response = self.client.get(reverse(views.admin_results))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['matches']), 5)
