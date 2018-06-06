# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from nmkapp import views
from nmkapp import models

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
        response = client.post(reverse(views.create_password), {'new_password1': 'maiev_shadowsong', 'new_password2': 'maiev SHADOWSONG'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        print(str(context['form'].errors['new_password2']))
        self.assertIsNotNone(context['form'])
        self.assertTrue('The two password fields didn&#39;t match.' in
                        str(context['form'].errors['new_password2']))

    def test_create_password_user_already_has_password(self):
        client = Client()
        user = User.objects.get(username='seki@mail.com')
        client.force_login(user)
        response = client.get(reverse(views.create_password))
        self.assertEqual(response.status_code, 302)
