# -*- coding: utf-8 -*-
import datetime

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class HomeTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.home))
        self.assertEqual(response.status_code, 302)

    @NmkUnitTestCase.assertNumQueriesLessThan(16)
    def test_no_active_round(self):
        """
        Test home view when there is no active rounds
        """
        # Remove current active round
        response = self.client.get('{}?set_inactive={}'.format(reverse(views.admin_rounds), 3))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['shots']), 0)
        self.assertEqual(len(context['messages']), 1)
        self.assertEqual(list(context['messages'])[0].message,
                         'There is no active round currently to place bets, try again later')

    def test_active_round_in_past(self):
        """
        Tests that player cannot play match from past
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))
        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertEqual(bet['time_left'], 'first match already started')
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertIsNone(bet['shots'][0].shot)

    def test_active_round_already_played(self):
        """
        Tests that player who already clicked "final answer" have proper data displayed
        """
        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertTrue('2d' in bet['time_left'])
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertEqual(bet['shots'][0].shot, 0)

    @NmkUnitTestCase.assertNumQueriesLessThan(35)
    def test_active_round_playable(self):
        """
        Tests that player who is eligible to play can actually play
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))
        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertTrue('2d' in bet['time_left'])
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNotNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertIsNone(bet['shots'][0].shot)

    def test_play_round_save_incomplete_save(self):
        """
        Tests when user do not submit all bets
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))

        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()

        response = self.client.post(reverse(views.home), {'save_3': None})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('You must place all bets', response.context['bets'][0]['form'].errors['__all__'][0])

    def test_play_round_save(self):
        """
        Tests that player who is eligible to play to save
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))

        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()

        response = self.client.post(reverse(views.home), {'save_3': None, '8_5': 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.home), response['location'])

        # Visit page again to see if our bets are saved
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNotNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertEqual(bet['shots'][0].shot, 2)

    def test_play_round_final_save(self):
        """
        Tests that player who is eligible to play to do final save
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))

        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()

        response = self.client.post(reverse(views.home), {'final_save_3': None, '8_5': 0})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.home), response['location'])

        # Visit page again to see if our bets are saved and we cannot play again
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertTrue('2d' in bet['time_left'])
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertEqual(bet['shots'][0].shot, 0)
