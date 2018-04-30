# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

from .nmk_unit_test_case import NmkUnitTestCase


class ResetPasswordTests(NmkUnitTestCase):
    def test_no_reset_code(self):
        client = Client()
        response = client.get(reverse(views.reset_password))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue('form' not in context)
        self.assertTrue('reset' not in context)
        self.assertTrue('email' not in context)
        self.assertTrue(context['nonvalid'])

    def test_wrong_reset_code(self):
        client = Client()
        response = client.get('{}?id={}'.format(reverse(views.reset_password), 'foo'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue('form' not in context)
        self.assertTrue('reset' not in context)
        self.assertTrue('email' not in context)
        self.assertTrue(context['nonvalid'])

    def test_land_reset_password(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'kokan@mail.com'})
        self.assertEqual(response.status_code, 200)
        reset_code = models.Player.objects.filter(user__email='kokan@mail.com')[0].reset_code
        response = client.get('{}?id={}'.format(reverse(views.reset_password), reset_code))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertFalse(context['reset'])
        self.assertEqual(context['email'], 'kokan@mail.com')
        self.assertFalse(context['nonvalid'])

    def test_reset_password(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'kokan@mail.com'})
        self.assertEqual(response.status_code, 200)
        reset_code = models.Player.objects.filter(user__email='kokan@mail.com')[0].reset_code
        response = client.post('{}?id={}'.format(reverse(views.reset_password), reset_code),
                               {'password': 'newpass', 'password2': 'newpass'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue(context['reset'])
        self.assertEqual(context['email'], 'kokan@mail.com')
        self.assertFalse(context['nonvalid'])

        self.assertTrue(self.client.login(username='kokan@mail.com', password='newpass'))

    def test_reset_password_password_too_short(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'kokan@mail.com'})
        self.assertEqual(response.status_code, 200)
        reset_code = models.Player.objects.filter(user__email='kokan@mail.com')[0].reset_code
        response = client.post('{}?id={}'.format(reverse(views.reset_password), reset_code),
                               {'password': 'foo', 'password2': 'foo'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue('Ensure this value has at least 5 characters (it has 3)' in
                        str(context['form'].errors['password']))
        self.assertTrue('Ensure this value has at least 5 characters (it has 3)' in
                        str(context['form'].errors['password2']))
        self.assertFalse(context['reset'])
        self.assertEqual(context['email'], 'kokan@mail.com')
        self.assertFalse(context['nonvalid'])

    def test_reset_password_passwords_different(self):
        client = Client()
        response = client.post(reverse(views.forgotpassword), {'email': 'kokan@mail.com'})
        self.assertEqual(response.status_code, 200)
        reset_code = models.Player.objects.filter(user__email='kokan@mail.com')[0].reset_code
        response = client.post('{}?id={}'.format(reverse(views.reset_password), reset_code),
                               {'password': 'newpass', 'password2': 'newpass2'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue('Passwords do not match' in
                        str(context['form'].errors['password2']))
        self.assertFalse(context['reset'])
        self.assertEqual(context['email'], 'kokan@mail.com')
        self.assertFalse(context['nonvalid'])
