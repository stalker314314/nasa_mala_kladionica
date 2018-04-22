# -*- coding: utf-8 -*-

from django.core import mail
from django.test import Client
from django.urls import reverse

from nmkapp import models,views

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminResultsChangeTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_results_change, args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki', password='12345'))
        response = client.get(reverse(views.admin_results_change, args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        response = self.client.get(reverse(views.admin_results_change, args=(1,)))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['match'].id, 1)
        self.assertIsNotNone(context['form'])

    def test_change_result(self):
        with self.settings(SEND_MAIL=True):
            response = self.client.post(reverse(views.admin_results_change, args=(5,)), {'score': '5:2'})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(reverse(views.admin_results), response['location'])
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, '[nmk] Uneti svi rezultati mečeva iz kola "Final"')

        match = models.Match.objects.filter(id=5)[0]
        self.assertEqual(match.result, 1)
        self.assertEqual(match.score, '5:2')
