# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class ResultsLeagueTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.results_league))
        self.assertEqual(response.status_code, 302)

    def test_league(self):
        """
        Test visiting league results page
        """
        response = self.client.get(reverse(views.results_league))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['groups']), 2)
        group_a = next(group for group in context['groups'] if group['label'] == 'A')
        self.assertEqual(len(group_a['league']), 2)
        self.assertEqual(group_a['league'][0], ['Team Best',  2, 1, 1, 0, 4])
        self.assertEqual(group_a['league'][1], ['Team Worst', 2, 0, 1, 1, 1])
        self.assertEqual(len(group_a['matches']), 2)
        match1 = next(match for match in group_a['matches'] if match.id == 1)
        self.assertEqual(match1.round.id, 1)
        self.assertEqual(match1.home_team.id, 1)
        self.assertEqual(match1.away_team.id, 2)
        self.assertEqual(match1.odd1, 1.5)
        self.assertEqual(match1.oddX, 2.3)
        self.assertEqual(match1.odd2, 3.4)
        self.assertEqual(match1.result, 1)
        self.assertEqual(match1.score, '1:0')
        match2 = next(match for match in group_a['matches'] if match.id == 3)
        self.assertEqual(match2.round.id, 2)
        self.assertEqual(match2.home_team.id, 2)
        self.assertEqual(match2.away_team.id, 1)
        self.assertEqual(match2.odd1, 4.0)
        self.assertEqual(match2.oddX, 4.0)
        self.assertEqual(match2.odd2, 4.0)
        self.assertEqual(match2.result, 0)
        self.assertEqual(match2.score, '1:1')

        group_b = next(group for group in context['groups'] if group['label'] == 'B')
        self.assertEqual(len(group_b['league']), 2)
        self.assertEqual(group_b['league'][0], ['Team Second', 2, 1, 1, 0, 4])
        self.assertEqual(group_b['league'][1], ['Team Third',  2, 0, 1, 1, 1])
        self.assertEqual(len(group_b['matches']), 2)
        match1 = next(match for match in group_b['matches'] if match.id == 2)
        self.assertEqual(match1.round.id, 1)
        self.assertEqual(match1.home_team.id, 3)
        self.assertEqual(match1.away_team.id, 4)
        self.assertEqual(match1.odd1, 2.0)
        self.assertEqual(match1.oddX, 3.0)
        self.assertEqual(match1.odd2, 4.0)
        self.assertEqual(match1.result, 2)
        self.assertEqual(match1.score, '1:3')
        match2 = next(match for match in group_b['matches'] if match.id == 4)
        self.assertEqual(match2.round.id, 2)
        self.assertEqual(match2.home_team.id, 4)
        self.assertEqual(match2.away_team.id, 3)
        self.assertEqual(match2.odd1, 5.0)
        self.assertEqual(match2.oddX, 5.0)
        self.assertEqual(match2.odd2, 5.0)
        self.assertEqual(match2.result, 0)
        self.assertEqual(match2.score, '0:0')
