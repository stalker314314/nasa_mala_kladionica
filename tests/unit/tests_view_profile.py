# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase, Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models


class ProfileTests(TestCase):
    fixtures = ['initial_data.json']

    def test_anon_user(self):
        self.client = Client()
        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        """
        Test profile view when user is logged
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertIsNotNone(context['form_new_group'])
        self.assertIsNotNone(context['form_add_group'])
        self.assertIsNotNone(context['form_add_group'])
        self.assertIsNotNone(len(context['groups']), 2)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])
        self.assertEqual(context['current_user'].id, 1)
