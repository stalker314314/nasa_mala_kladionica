# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase, Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models


class HomeTests(TestCase):
    fixtures = ['initial_data.json']

    def test_anon_user(self):
        self.client = Client()
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 302)

    def test_no_active_round(self):
        """
        Test home view when there is no active rounds
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['shots']), 0)
        self.assertEqual(len(context['messages']), 1)
        self.assertEqual(list(context['messages'])[0].message,
                         'Trenutno nema aktivnog kola za klađenje, pokušaj kasnije')

    def test_active_round_in_past(self):
        """
        Tests that player cannot play match from past
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='gumi', password='12345'))
        round = models.Round.objects.filter(name='Final')[0]
        round.active = True
        round.save()
        response = self.client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context['bets']), 1)
        bet = context['bets'][0]
        self.assertEqual(bet['time_left'], 'prvi meč već počeo')
        self.assertEqual(bet['round'].id, 3)
        self.assertIsNone(bet['form'])
        self.assertEqual(len(bet['shots']), 1)
        self.assertEqual(bet['shots'][0].match.id, 5)
        self.assertIsNone(bet['shots'][0].shot)

    def test_active_round_already_played(self):
        """
        Tests that player who already clicked "final answer" have proper data displayed
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
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