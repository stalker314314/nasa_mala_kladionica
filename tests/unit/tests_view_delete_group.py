# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views

from .nmk_unit_test_case import NmkUnitTestCase


class DeleteGroupTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.group_delete, args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_visit_delete_group(self):
        """
        Test delete group view when user is logged
        """
        response = self.client.get(reverse(views.group_delete, args=(1,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNone(context['error'])
        self.assertIsNotNone(context['group'])
        self.assertEqual(context['group'].id, 1)

    def test_post_delete_group_wrong_call(self):
        response = self.client.post(reverse(views.group_delete, args=(1,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNone(context['error'])
        self.assertIsNotNone(context['group'])
        self.assertEqual(context['group'].id, 1)

    def test_post_delete_group_denied_deletion(self):
        response = self.client.post(reverse(views.group_delete, args=(1,)), {'0': None})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.profile), response['location'])

    def test_post_delete_group_accepted_deletion(self):
        response = self.client.post(reverse(views.group_delete, args=(1,)), {'1': None})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse(views.profile), response['location'])

    def test_visit_delete_group_which_does_not_exist(self):
        response = self.client.get(reverse(views.group_delete, args=(10,)))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_group_which_does_not_exist(self):
        response = self.client.post(reverse(views.group_delete, args=(10,)), {'1': None})
        self.assertEqual(response.status_code, 404)

    def test_visit_delete_group_not_a_member(self):
        response = self.client.get(reverse(views.group_delete, args=(3,)))
        self.assertEqual(response.status_code, 404)

    def test_post_visit_delete_group_not_a_member(self):
        response = self.client.post(reverse(views.group_delete, args=(3,)), {'1': None})
        self.assertEqual(response.status_code, 404)

    def test_post_visit_delete_group_not_an_owner(self):
        client = Client()
        self.assertTrue(client.login(username='gumi', password='12345'))
        response = client.post(reverse(views.group_delete, args=(2,)), {'1': None})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['error'],
                         'Ne možeš da izbrišeš ekipu koju nisi ti napravio, možeš samo da izađeš iz nje.')
        self.assertIsNotNone(context['group'])
        self.assertEqual(context['group'].id, 2)
