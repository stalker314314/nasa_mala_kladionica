# -*- coding: utf-8 -*-

import datetime

from django.test import Client
from django.urls import reverse
from django.conf import settings

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class ProfileTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        """
        Test profile view when user is logged
        """
        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertEqual(context['current_user'].id, 1)

    def test_change_language(self):
        """
        Test changing a user's language
        """
        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['form'].instance.language, settings.LANGUAGE_CODE)
        language_to_change_to = 'sr'
        self.assertNotEqual(context['form'].instance.language, language_to_change_to,
                            'Test is not valid as we are changing language to the same one')

        response = self.client.post(reverse(views.profile), {'language': language_to_change_to, 'timezone': 'UTC',
                                                             'odd_format': 1, 'profile_change': ''})
        self.assertEqual(response.status_code, 200)

        # Check that message is in new language
        context = response.context
        self.assertEqual(len(context['messages']), 1)
        self.assertEqual(list(context['messages'])[0].message, 'Подешавања успешно сачувана')

        # Make sure we are using new language
        self.assertEqual(models.Player.objects.filter(user__id=1).get().language, language_to_change_to)

        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['form'].instance.language, language_to_change_to)

    def test_change_timezone(self):
        """
        Test changing timezone.
        TODO: add check that proper times are being shown in templates
        """
        response = self.client.post(reverse(views.profile), {'language': 'en', 'timezone': 'Australia/Currie',
                                                             'odd_format': 1, 'profile_change': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Player.objects.filter(user__id=1).get().timezone.zone, 'Australia/Currie')

    def test_change_timezone_invalid(self):
        response = self.client.post(reverse(views.profile), {'language': 'en', 'timezone': 'Invalid/Timezone',
                                                             'profile_change': ''})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['form'].errors['timezone'][0],
                         'Select a valid choice. Invalid/Timezone is not one of the available choices.')

    def test_change_odd_format(self):
        """
        Test changing format of odds shown
        TODO: add check that odd format are properly shown on roundstandings too (and when betting is not allowed)
        """
        # First make round still playable by player 'gumi'
        nmk_round = models.Round.objects.filter(name='Final')[0]
        nmk_round.active = True
        nmk_round.save()
        match = models.Match.objects.filter(id=5)[0]
        match.start_time = datetime.datetime.now() + datetime.timedelta(days=2, hours=12)
        match.save()
        # We will use 'gumi' player in this test, log in as 'gumi'
        client = Client()
        self.assertTrue(client.login(username='gumi', password='12345'))

        # Check how odds are formatted before we change them to be fractional (they should be decimal)
        response = client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual('1.5', context['bets'][0]['form'].fields['8_5'].widget.choices[0][1])
        self.assertEqual('5.0', context['bets'][0]['form'].fields['8_5'].widget.choices[1][1])
        self.assertEqual('1.23', context['bets'][0]['form'].fields['8_5'].widget.choices[2][1])

        # Change odd format to fractional
        self.assertEqual(models.Player.objects.filter(user__id=2).get().odd_format, models.Player.DECIMAL)
        response = client.post(reverse(views.profile), {'language': 'en', 'timezone': 'UTC',
                                                        'odd_format': models.Player.FRACTIONAL,
                                                        'profile_change': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Player.objects.filter(user__id=2).get().odd_format, models.Player.FRACTIONAL)

        # Check how odds are formatted now
        response = client.get(reverse(views.home))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual('1/2', context['bets'][0]['form'].fields['8_5'].widget.choices[0][1])
        self.assertEqual('4/1', context['bets'][0]['form'].fields['8_5'].widget.choices[1][1])
        self.assertEqual('23/100', context['bets'][0]['form'].fields['8_5'].widget.choices[2][1])
