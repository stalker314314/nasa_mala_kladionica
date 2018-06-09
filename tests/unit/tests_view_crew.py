# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import models
from nmkapp import views
from .nmk_unit_test_case import NmkUnitTestCase


class CrewTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.crew))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        """
        Test crew view when user is logged
        """
        response = self.client.get(reverse(views.crew))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIsNotNone(context['form_new_group'])
        self.assertIsNotNone(context['form_add_group'])
        self.assertIsNotNone(len(context['groups']), 2)
        self.assertTrue(1 in [group.id for group in context['groups']])
        self.assertTrue(2 in [group.id for group in context['groups']])
        self.assertEqual(context['current_user'].id, 1)

    def test_create_group(self):
        """
        Test group creation
        """
        response = self.client.post(reverse(views.crew), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)

        new_group = models.Group.objects.filter(name='foobar')[0]
        response = self.client.get(reverse(views.crew))
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
        # Create additional group as kokan
        response = self.client.post(reverse(views.crew), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)
        new_group = models.Group.objects.filter(name='foobar')[0]

        # Login gumi and add gumi to newly created group
        self.assertTrue(self.client.login(username='gumi@mail.com', password='12345'))
        response = self.client.post(reverse(views.crew), {'add_to_group': None, 'key': new_group.group_key})
        self.assertEqual(response.status_code, 200)

        # Leave gumi from group
        response = self.client.post(reverse(views.group_leave, args=(new_group.id,)))
        self.assertEqual(response.status_code, 200)

        # Check groups in which Gumi is
        response = self.client.post(reverse(views.crew), {'new_group': None, 'name': 'foobar'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(len(context['groups']), 1)
        self.assertTrue(2 in [group.id for group in context['groups']])
