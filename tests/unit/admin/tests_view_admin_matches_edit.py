# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import models, views


from ..nmk_unit_test_case import NmkUnitTestCase


class AdminMatchesEditTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_matches_edit))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
        response = client.get(reverse(views.admin_matches_edit))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        response = self.client.get(reverse(views.admin_matches_edit))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])

    def test_add_match(self):
        response = self.client.post(reverse(views.admin_rounds_edit), {'name': 'Final2', 'group_type': 'Cup'})
        self.assertEqual(response.status_code, 302)
        rounds = self._get_all_rounds()
        new_round_id = rounds[3].id

        response = self.client.post(reverse(views.admin_matches_edit), {
            'home_team': 1,
            'away_team': 2,
            'start_time': '2020-01-01',
            'round': new_round_id,
            'odd1': 4.0,
            'oddX': 5.0,
            'odd2': 6.0
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.admin_matches), response['location'])

        self.assertEqual(len(models.Match.objects.filter(round=new_round_id)), 1)
