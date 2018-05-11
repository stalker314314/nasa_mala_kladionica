# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class StandingsTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.standings))
        self.assertEqual(response.status_code, 302)

    @NmkUnitTestCase.assertNumQueriesLessThan(15)
    def test_regular_user(self):
        """
        Test visiting standings page
        """
        response = self.client.get(reverse(views.standings))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.check_full_standings_context(context)

    def check_full_standings_context(self, context):
        self.assertEqual(len(context['rounds']), 3)
        self.assertTrue(context['rounds'][0].id, 1)
        self.assertTrue(context['rounds'][1].id, 2)
        self.assertTrue(context['rounds'][2].id, 3)
        self.assertEqual(len(context['groups']), 2)
        self.assertTrue(1 in [g.id for g in context['groups']])
        self.assertTrue(2 in [g.id for g in context['groups']])
        self.assertEqual(context['selected_group'], '')
        self.assertEqual(len(context['standings']), 3)
        standings = context['standings']
        self.assertEqual(standings[0][0].user.id, 1)
        self.assertEqual(standings[0][0].user.email, 'kokan@mail.com')
        self.assertEqual(standings[0][1], [1.5, 9.0, 0.0])

        self.assertEqual(standings[1][0].user.id, 3)
        self.assertEqual(standings[1][0].user.email, 'seki@mail.com')
        self.assertEqual(standings[1][1], [0.0, 0.0, 0.0])

        self.assertEqual(standings[2][0].user.id, 2)
        self.assertEqual(standings[2][0].user.email, 'gumi@mail.com')
        self.assertEqual(standings[2][1], [0.0, 0.0, 0.0])

    @NmkUnitTestCase.assertNumQueriesLessThan(15)
    def test_other_group(self):
        link_with_group = '{}?group=kokangumi'.format(reverse(views.standings))
        response = self.client.get(link_with_group)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['rounds']), 3)
        self.assertTrue(context['rounds'][0].id, 1)
        self.assertTrue(context['rounds'][1].id, 2)
        self.assertTrue(context['rounds'][2].id, 3)
        self.assertEqual(len(context['groups']), 2)
        self.assertTrue(1 in [g.id for g in context['groups']])
        self.assertTrue(2 in [g.id for g in context['groups']])
        self.assertEqual(context['selected_group'], 'kokangumi')
        self.assertEqual(len(context['standings']), 2)
        standings = context['standings']
        self.assertEqual(standings[0][0].user.id, 1)
        self.assertEqual(standings[0][0].user.email, 'kokan@mail.com')
        self.assertEqual(standings[0][1], [1.5, 9.0, 0.0])

        self.assertEqual(standings[1][0].user.id, 2)
        self.assertEqual(standings[1][0].user.email, 'gumi@mail.com')
        self.assertEqual(standings[1][1], [0.0, 0.0, 0.0])

    def test_other_group_not_visible(self):
        link_with_group = '{}?group=gumiseki'.format(reverse(views.standings))
        response = self.client.get(link_with_group)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.check_full_standings_context(context)
