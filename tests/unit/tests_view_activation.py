# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class ActivationTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.activation))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNone(context['player'])
        self.assertFalse(context['success'])

    def test_anon_user_bad_id(self):
        client = Client()
        response = client.get('{}?id={}'.format(reverse(views.activation), 'foo'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNone(context['player'])
        self.assertFalse(context['success'])

    def test_anon_user_activation(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'username': 'foo',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'email': 'foo@bar.com',
            'password': 'foo123'
        })
        self.assertEqual(response.status_code, 200)
        activation_code = models.Player.objects.filter(user__username='foo')[0].activation_code

        client = Client()
        response = client.get('{}?id={}'.format(reverse(views.activation), activation_code))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['player'])
        self.assertEqual(context['player'].user.username, 'foo')
        self.assertTrue(context['success'])
