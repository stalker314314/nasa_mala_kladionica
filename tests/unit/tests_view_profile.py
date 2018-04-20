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

    def test_create_group(self):
        """
        Test group creation
        """
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        response = self.client.post(reverse(views.profile), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)

        new_group = models.Group.objects.filter(name='foobar')[0]
        response = self.client.get(reverse(views.profile))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(len(context['groups']), 3)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])
        self.assertTrue(new_group.id in [group.id for group in context['groups']])

    def test_leave_group(self):
        """
        Test leaving group
        """
        # CReate additional group as kokan
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan', password='12345'))
        response = self.client.post(reverse(views.profile), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)
        new_group = models.Group.objects.filter(name='foobar')[0]

        # Login gumi and add gumi to newly created group
        self.assertTrue(self.client.login(username='gumi', password='12345'))
        response = self.client.post(reverse(views.profile), {'add_to_group': None, 'key': new_group.group_key})
        self.assertEqual(response.status_code, 200)

        # Leave gumi from group
        response = self.client.post(reverse(views.group_leave, args=(new_group.id,)))
        self.assertEqual(response.status_code, 200)

        # Check groups in which Gumi is
        response = self.client.post(reverse(views.profile), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(len(context['groups']), 1)
        self.assertTrue(2 in [group.id for group in context['groups']])
