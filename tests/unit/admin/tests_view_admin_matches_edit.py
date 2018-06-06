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
        self.assertEqual(reverse(views.admin_matches), response['location'] + '/')

        self.assertEqual(len(models.Match.objects.filter(round=new_round_id)), 1)

    def test_add_match_same_teams(self):
        response = self.client.post(reverse(views.admin_rounds_edit), {'name': 'Final2', 'group_type': 'Cup'})
        self.assertEqual(response.status_code, 302)
        rounds = self._get_all_rounds()
        new_round_id = rounds[3].id

        response = self.client.post(reverse(views.admin_matches_edit), {
            'home_team': 1,
            'away_team': 1,
            'start_time': '2020-01-01',
            'round': new_round_id,
            'odd1': 4.0,
            'oddX': 5.0,
            'odd2': 6.0
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Team cannot play match against itself' in str(response.context['form'].errors))
        self.assertEqual(len(models.Match.objects.filter(round=new_round_id)), 0)

    def test_add_match_betting_already_done(self):
        response = self.client.post(reverse(views.admin_matches_edit), {
            'home_team': 1,
            'away_team': 2,
            'start_time': '2020-01-01',
            'round': 3,
            'odd1': 4.0,
            'oddX': 5.0,
            'odd2': 6.0
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You cannot add new matches in this round, as some players already placed bets in this round'
                        in str(response.context['form'].errors))
        self.assertEqual(len(models.Match.objects.filter(round=3)), 1)

    def test_add_match_team_already_plays_same_round(self):
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
        self.assertEqual(len(models.Match.objects.filter(round=new_round_id)), 1)

        # try all combinations of home/away team and who that team is
        expected_messages = ['Team Team Best already plays in this round', 'Team Team Worst already plays in this round']
        for team1, team2, message_index in [(1,3,0), (3,1,0), (2,3,1), (3,2,1)]:
            response = self.client.post(reverse(views.admin_matches_edit), {
                'home_team': team1,
                'away_team': team2,
                'start_time': '2020-01-01',
                'round': new_round_id,
                'odd1': 4.0,
                'oddX': 5.0,
                'odd2': 6.0
                })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(expected_messages[message_index] in str(response.context['form'].errors))
            self.assertEqual(len(models.Match.objects.filter(round=new_round_id)), 1)
