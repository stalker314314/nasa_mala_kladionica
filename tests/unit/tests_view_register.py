# -*- coding: utf-8 -*-

from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

class RegisterTests(TestCase):
    def test_register_visit(self):
        self.client = Client()
        response = self.client.get(reverse(views.register))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertFalse(context['registered'])
        self.assertTrue(context['no_menu'])

    def test_register_empty_form(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', u'This field is required.')
        self.assertFormError(response, 'form', 'first_name', u'This field is required.')
        self.assertFormError(response, 'form', 'last_name', u'This field is required.')
        self.assertFormError(response, 'form', 'email', u'This field is required.')
        self.assertFormError(response, 'form', 'password', u'This field is required.')

    def test_register(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'username': 'foo',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'email': 'foo@bar.com',
            'password': 'foo123'
        })
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['registered'])
        self.assertTrue(context['no_menu'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[nmk] Registracija na NMK uspešna')

        users = models.User.objects.filter(username='foo')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'foo@bar.com')
        self.assertFalse(users[0].is_active)
        self.assertFalse(users[0].is_staff)
        self.assertFalse(users[0].is_superuser)
        self.assertFalse(users[0].player.in_money)
        self.assertEqual(users[0].player.points, 0)
        self.assertTrue(users[0].player.send_mail)

    def test_register_already_exists(self):
        # TODO: this currently works, it shouldn't
        pass

    def test_register_after_competition_started(self):
        # TODO: this can work only after competition start time is extract as dynamic thing
        pass

    def test_register_logged_user(self):
        # TODO: fix
        pass
