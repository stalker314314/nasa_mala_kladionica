# -*- coding: utf-8 -*-

from django.core import mail
from django.test import Client
from django.urls import reverse

from nmkapp import models, views

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminResultsChangeTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_results_change, args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
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
            self.assertEqual(len(mail.outbox), 3)
            self.assertEqual(mail.outbox[0].subject, '[sharkz.bet] All results from round "Final" received')

        match = models.Match.objects.filter(id=5).get()
        self.assertEqual(match.result, 1)
        self.assertEqual(match.score, '5:2')

    def test_change_result_wrong_format(self):
        all_various_scores_that_can_fail = ['', '1', 'foo', '52']
        for score in all_various_scores_that_can_fail:
            with self.settings(SEND_MAIL=True):
                response = self.client.post(reverse(views.admin_results_change, args=(5,)), {'score': score})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 0)

            self.assertEqual(response.status_code, 200)
            self.assertTrue('There should be colon between two numbers' in str(response.context['form'].errors))
            match = models.Match.objects.filter(id=5).get()
            self.assertEqual(match.result, None)

        all_various_scores_that_cannot_be_parsed = [':', '1:', ':1', 'foo:1', '1:foo']
        for score in all_various_scores_that_cannot_be_parsed:
            with self.settings(SEND_MAIL=True):
                response = self.client.post(reverse(views.admin_results_change, args=(5,)), {'score': score})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 0)

            self.assertEqual(response.status_code, 200)
            self.assertTrue('Cannot parse numbers in result' in str(response.context['form'].errors))
            match = models.Match.objects.filter(id=5).get()
            self.assertEqual(match.result, None)
