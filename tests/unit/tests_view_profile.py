# -*- coding: utf-8 -*-

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

        response = self.client.post(reverse(views.profile), {'language': language_to_change_to, 'profile_change': ''})
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
