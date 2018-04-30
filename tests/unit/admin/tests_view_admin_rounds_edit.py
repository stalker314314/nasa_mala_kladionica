# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminRoundsEditTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_rounds_edit))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
        response = client.get(reverse(views.admin_rounds_edit))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        response = self.client.get(reverse(views.admin_rounds_edit))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])

    def test_add_rounds(self):
        response = self.client.post(reverse(views.admin_rounds_edit), {'name': 'Final2', 'group_type': 'Cup'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.admin_rounds), response['location'])

        # Check that there is 4 rounds now
        response = self.client.get(reverse(views.admin_rounds))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['rounds']), 4)
