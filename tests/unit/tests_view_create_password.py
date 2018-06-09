# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.views import password_change
from django.test import Client
from django.urls import reverse

from nmkapp import views
from .nmk_unit_test_case import NmkUnitTestCase


class CreatePasswordTests(NmkUnitTestCase):
    def setUp(self):
        super().setUp()
        user = User.objects.create_user(username='maiev',
                                        email='maiev@shadowsong.com')
        user.set_unusable_password()
        user.save()

    def test_land_create_password(self):
        client = Client()
        user = User.objects.get(username='maiev')
        client.force_login(user)
        response = client.get(reverse(views.create_password))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])

    def test_create_password_too_short(self):
        client = Client()
        user = User.objects.get(username='maiev')
        client.force_login(user)
        response = client.post(reverse(views.create_password), {'new_password1': 'a', 'new_password2': 'a'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        self.assertTrue('Ensure this value has at least 5 characters (it has 1).' in
                        str(context['form'].errors['new_password1']))
        self.assertTrue('Ensure this value has at least 5 characters (it has 1)' in
                        str(context['form'].errors['new_password2']))

    def test_create_password_passwords_different(self):
        client = Client()
        user = User.objects.get(username='maiev')
        client.force_login(user)
        response = client.post(reverse(views.create_password), {
            'new_password1': 'maiev_shadowsong', 'new_password2': 'maiev SHADOWSONG'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        print(str(context['form'].errors['new_password2']))
        self.assertIsNotNone(context['form'])
        self.assertTrue('The two password fields didn&#39;t match.' in
                        str(context['form'].errors['new_password2']))

    def test_create_password_user_already_has_password(self):
        client = Client()
        client.login(username='seki@mail.com', password='12345')
        response = client.get(reverse(views.create_password))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(password_change), response['location'])

    def test_create_password_anon_user(self):
        pass

    def test_create_password(self):
        client = Client()
        user = User.objects.get(username='maiev')
        client.force_login(user)
        response = client.get(reverse(views.create_password))
        self.assertEqual(response.status_code, 200)
        response = client.post(reverse(views.create_password),
                               {'new_password1': 'Super Secure Password', 'new_password2': 'Super Secure Password'})
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(self.client.login(username='maiev', password='Super Secure Password'))
        client.login(username='maiev', password='Super Secure Password')
        response = client.get(reverse(views.create_password))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(password_change), response['location'])
