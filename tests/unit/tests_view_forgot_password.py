# -*- coding: utf-8 -*-

from django.core import mail
from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class ForgotPasswordTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.forgotpassword))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertFalse(context['reset'])

    def test_reset_password(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'branko@kokanovi.com'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['reset'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['branko@kokanovi.com'])
        self.assertEqual(mail.outbox[0].subject, '[nmk] Zahtev za resetovanjem lozinke')

    def test_reset_password_unknown_mail(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'branko@kokanovi2.com'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertFalse(context['reset'])
        self.assertEqual(len(mail.outbox), 0)
