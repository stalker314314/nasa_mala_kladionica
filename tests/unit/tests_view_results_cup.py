# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class ResultsCupTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.results_cup))
        self.assertEqual(response.status_code, 302)

    def test_results_cup(self):
        """
        Test cup results view
        """
        response = self.client.get(reverse(views.results_cup))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['rounds']), 1)
        round = context['rounds'][0]
        self.assertEqual(round[0].id, 3)
        self.assertEqual(round[0].name, 'Final')
        self.assertEqual(len(round[1]), 1)
        match = round[1][0]
        self.assertEqual(match.id, 5)
        self.assertEqual(match.round.id, 3)
        self.assertEqual(match.home_team.id, 1)
        self.assertEqual(match.away_team.id, 3)
        self.assertEqual(match.odd1, 5.0)
        self.assertEqual(match.oddX, 5.0)
        self.assertEqual(match.odd2, 5.0)
        self.assertIsNone(match.result)
        self.assertEqual(match.score, '')
