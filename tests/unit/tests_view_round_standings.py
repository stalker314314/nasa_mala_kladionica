# -*- coding: utf-8 -*-

import datetime

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class RoundStandingsTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.round_standings, args=(1,)))
        self.assertEqual(response.status_code, 302)

    @NmkUnitTestCase.assertNumQueriesLessThan(20)
    def test_regular_user_round_1(self):
        """
        Test visiting standings page
        """
        response = self.client.get(reverse(views.round_standings, args=(1,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])

        self.assertEqual(context['selected_group'], '')

        self.assertEqual(context['round'].id, 1)

        self.assertEqual(len(context['matches']), 2)
        self.assertEqual(context['matches'][0].id, 1)
        self.assertEqual(context['matches'][1].id, 2)

        self.assertEqual(len(context['round_standings']), 3)
        rs = context['round_standings']
        self.assertEqual(rs[0]['position'], 1)
        self.assertEqual(len(rs[0]['shots']), 2)
        self.assertEqual(rs[0]['shots'][0]['shot'], 1)
        self.assertEqual(rs[0]['shots'][0]['match_result'], 1)
        self.assertEqual(rs[0]['shots'][1]['shot'], 1)
        self.assertEqual(rs[0]['shots'][1]['match_result'], 2)
        self.assertEqual(rs[0]['user_round']['email'], 'kokan@mail.com')
        self.assertEqual(rs[0]['user_round']['points'], 1.5)
        self.assertFalse(rs[0]['user_round']['in_money'])

        self.assertEqual(rs[1]['user_round']['email'], 'gumi@mail.com')
        self.assertEqual(rs[1]['user_round']['points'], 0.0)
        self.assertFalse(rs[1]['user_round']['in_money'])
        self.assertEqual(rs[1]['shots'][0]['shot'], 0)
        self.assertEqual(rs[1]['shots'][0]['match_result'], 1)
        self.assertEqual(rs[1]['shots'][1]['shot'], 0)
        self.assertEqual(rs[1]['shots'][1]['match_result'], 2)

        self.assertEqual(rs[2]['user_round']['email'], 'seki@mail.com')
        self.assertEqual(rs[2]['user_round']['points'], 0.0)
        self.assertFalse(rs[2]['user_round']['in_money'])
        self.assertEqual(rs[2]['shots'][0]['shot'], '')
        self.assertEqual(rs[2]['shots'][0]['match_result'], 1)
        self.assertEqual(rs[2]['shots'][1]['shot'], '')
        self.assertEqual(rs[2]['shots'][1]['match_result'], 2)

        self.assertEqual(len(context['groups']), 2)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])

    @NmkUnitTestCase.assertNumQueriesLessThan(20)
    def test_regular_user_round_1_other_group(self):
        """
        Test visiting standings page with some other group
        """
        link_with_group = '{}?group=kokangumi'.format(reverse(views.round_standings, args=(1,)))
        response = self.client.get(link_with_group)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])

        self.assertEqual(context['selected_group'], 'kokangumi')

        self.assertEqual(context['round'].id, 1)

        self.assertEqual(len(context['matches']), 2)
        self.assertEqual(context['matches'][0].id, 1)
        self.assertEqual(context['matches'][1].id, 2)

        self.assertEqual(len(context['round_standings']), 2)
        rs = context['round_standings']
        self.assertEqual(rs[0]['position'], 1)
        self.assertEqual(len(rs[0]['shots']), 2)
        self.assertEqual(rs[0]['shots'][0]['shot'], 1)
        self.assertEqual(rs[0]['shots'][0]['match_result'], 1)
        self.assertEqual(rs[0]['shots'][1]['shot'], 1)
        self.assertEqual(rs[0]['shots'][1]['match_result'], 2)
        self.assertEqual(rs[0]['user_round']['email'], 'kokan@mail.com')
        self.assertEqual(rs[0]['user_round']['points'], 1.5)
        self.assertFalse(rs[0]['user_round']['in_money'])

        self.assertEqual(rs[1]['user_round']['email'], 'gumi@mail.com')
        self.assertEqual(rs[1]['user_round']['points'], 0.0)
        self.assertFalse(rs[1]['user_round']['in_money'])
        self.assertEqual(rs[1]['shots'][0]['shot'], 0)
        self.assertEqual(rs[1]['shots'][0]['match_result'], 1)
        self.assertEqual(rs[1]['shots'][1]['shot'], 0)
        self.assertEqual(rs[1]['shots'][1]['match_result'], 2)

        self.assertEqual(len(context['groups']), 2)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])

    @NmkUnitTestCase.assertNumQueriesLessThan(20)
    def test_regular_user_round_2(self):
        """
        Test visiting standings page
        """
        response = self.client.get(reverse(views.round_standings, args=(2,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])

        self.assertEqual(context['selected_group'], '')

        self.assertEqual(context['round'].id, 2)

        self.assertEqual(len(context['matches']), 2)
        self.assertEqual(context['matches'][0].id, 3)
        self.assertEqual(context['matches'][1].id, 4)

        self.assertEqual(len(context['round_standings']), 3)
        rs = context['round_standings']
        self.assertEqual(rs[0]['position'], 1)

        self.assertEqual(rs[0]['user_round']['email'], 'kokan@mail.com')
        self.assertEqual(rs[0]['user_round']['points'], 9.0)
        self.assertFalse(rs[0]['user_round']['in_money'])
        self.assertEqual(len(rs[0]['shots']), 2)
        self.assertEqual(rs[0]['shots'][0]['shot'], 0)
        self.assertEqual(rs[0]['shots'][0]['match_result'], 0)
        self.assertEqual(rs[0]['shots'][1]['shot'], 0)
        self.assertEqual(rs[0]['shots'][1]['match_result'], 0)

        self.assertEqual(rs[1]['user_round']['email'], 'gumi@mail.com')
        self.assertEqual(rs[1]['user_round']['points'], 0.0)
        self.assertFalse(rs[1]['user_round']['in_money'])
        self.assertEqual(rs[1]['shots'][0]['shot'], 2)
        self.assertEqual(rs[1]['shots'][0]['match_result'], 0)
        self.assertEqual(rs[1]['shots'][1]['shot'], 2)
        self.assertEqual(rs[1]['shots'][1]['match_result'], 0)

        self.assertEqual(rs[2]['user_round']['email'], 'seki@mail.com')
        self.assertEqual(rs[2]['user_round']['points'], 0.0)
        self.assertFalse(rs[2]['user_round']['in_money'])
        self.assertEqual(rs[2]['shots'][0]['shot'], '')
        self.assertEqual(rs[2]['shots'][0]['match_result'], 0)
        self.assertEqual(rs[2]['shots'][1]['shot'], '')
        self.assertEqual(rs[2]['shots'][1]['match_result'], 0)

        self.assertEqual(len(context['groups']), 2)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])

    def test_round_standings_not_visible(self):
        # First move date of final match to future
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()

        client = Client()
        self.assertTrue(client.login(username='gumi@mail.com', password='12345'))
        response = client.get(reverse(views.round_standings, args=(3,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertFalse(context['can_see_standings'])
        self.assertEqual(context['selected_group'], '')
        self.assertEqual(context['round'].id, 3)
        self.assertEqual(len(context['groups']), 2)
        self.assertEqual(len(context['round_standings']), 0)

    def test_round_visible_even_if_not_played(self):
        # Make sure this user didn't play this round
        self.assertFalse(models.UserRound.objects.filter(user__username='seki@mail.com', round=1)[0].shot_allowed)
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
        response = client.get(reverse(views.round_standings, args=(1,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])
        self.assertEqual(context['selected_group'], '')
        self.assertEqual(context['round'].id, 1)
        self.assertEqual(len(context['groups']), 1)
        self.assertEqual(len(context['round_standings']), 3)

    def test_round_visible_because_played_even_in_future(self):
        # First move date of final match to future
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()

        client = Client()
        self.assertTrue(client.login(username='kokan@mail.com', password='12345'))
        response = client.get(reverse(views.round_standings, args=(3,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])
        self.assertEqual(context['selected_group'], '')
        self.assertEqual(context['round'].id, 3)
        self.assertEqual(len(context['groups']), 2)
        self.assertEqual(len(context['round_standings']), 3)

    def test_round_other_groups_not_visible(self):
        """
        Test visiting standings page giving group name that user is not part of.
        In this case, there is no error for user, just empty group is used instead.
        """
        link_with_group = '{}?group=gumiseki'.format(reverse(views.round_standings, args=(1,)))
        response = self.client.get(link_with_group)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue(context['can_see_standings'])
        self.assertEqual(context['selected_group'], '')
        self.assertEqual(context['round'].id, 1)
        self.assertEqual(len(context['matches']), 2)
        self.assertEqual(len(context['round_standings']), 3)
        self.assertEqual(len(context['groups']), 2)
