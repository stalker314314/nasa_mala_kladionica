# -*- coding: utf-8 -*-

from django.core import mail
from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class RegisterTests(NmkUnitTestCase):
    def test_register_visit(self):
        client = Client()
        response = client.get(reverse(views.register))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['no_menu'])

    def test_register_empty_form(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'display_name', u'This field is required.')
        self.assertFormError(response, 'form', 'email', u'This field is required.')
        self.assertFormError(response, 'form', 'password', u'This field is required.')

    def test_register(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'display_name': 'Foo',
            'email': 'foo@bar.com',
            'password': 'foo123',
            'accept_terms': True,
            'over_18': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.register_success), response['location'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[sharkz.bet] Registration successful')

        users = models.User.objects.filter(email='foo@bar.com')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'foo@bar.com')
        self.assertEqual(users[0].first_name, 'Foo')
        self.assertEqual(users[0].last_name, '')
        self.assertFalse(users[0].is_active)
        self.assertFalse(users[0].is_staff)
        self.assertFalse(users[0].is_superuser)
        self.assertFalse(users[0].player.in_money)
        self.assertEqual(users[0].player.points, 0)
        self.assertTrue(users[0].player.send_mail_new_round)
        self.assertTrue(users[0].player.send_mail_reminder)
        self.assertTrue(users[0].player.send_mail_round_started)
        self.assertTrue(users[0].player.send_mail_results_available)

    def test_register_accept_terms_invalid(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'display_name': 'Foo2',
            'email': 'newmail@mail.com',
            'password': 'foo123',
            'over_18': True
        })
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['no_menu'])
        self.assertEqual('You have to accept terms and conditions to register',
                         context['form'].errors['accept_terms'][0])
        self.assertEqual(len(models.User.objects.filter(email='newmail@mail.com')), 0)

    def test_register_over_18_invalid(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'display_name': 'Foo2',
            'email': 'newmail@mail.com',
            'password': 'foo123',
            'accept_terms': True
        })
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['no_menu'])
        self.assertEqual('You must be over 18 to play on sharkz.bet', context['form'].errors['over_18'][0])
        self.assertEqual(len(models.User.objects.filter(email='newmail@mail.com')), 0)

    def test_register_email_already_exists(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'display_name': 'Foo2',
            'email': 'gumi@mail.com',
            'password': 'foo123',
            'accept_terms': True,
            'over_18': True
        })
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['no_menu'])
        self.assertEqual('This e-mail address already exists. If this is your e-mail, please reset password.',
                         context['form'].errors['email'][0])
        self.assertEqual(len(models.User.objects.filter(email='gumi@mail.com')), 1)

    def test_register_display_name_already_exists(self):
        self.client = Client()
        response = self.client.post(reverse(views.register), {
            'display_name': '@ILIJA JANKOVIC',
            'email': 'foo@bar.com',
            'password': 'foo123',
            'accept_terms': True,
            'over_18': True
        })
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['no_menu'])
        self.assertEqual(
            'This display name is already taken. If this is your display name by any chance, please log in.',
            context['form'].errors['display_name'][0])
        self.assertEqual(len(models.User.objects.filter(email='foo@bar.com')), 0)

    def test_register_after_competition_started(self):
        # TODO: this can work only after competition start time is extract as dynamic thing
        pass
