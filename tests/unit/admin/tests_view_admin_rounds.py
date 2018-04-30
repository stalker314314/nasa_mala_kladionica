# -*- coding: utf-8 -*-

from django.core import mail
from django.test import Client
from django.urls import reverse

from nmkapp import views

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminRoundsTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_rounds))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki@mail.com', password='12345'))
        response = client.get(reverse(views.admin_rounds))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        rounds = self._get_all_rounds()
        self.assertEqual(len(rounds), 3)
        self.assertTrue(1 in [nmkround.id for nmkround in rounds])
        self.assertTrue(2 in [nmkround.id for nmkround in rounds])
        self.assertTrue(3 in [nmkround.id for nmkround in rounds])

    def test_round_set_active(self):
        response = self.client.post(reverse(views.admin_rounds_edit), {'name': 'Final2', 'group_type': 'Cup'})
        self.assertEqual(response.status_code, 302)
        rounds = self._get_all_rounds()
        new_round_id = rounds[3].id

        with self.settings(SEND_MAIL=True):
            response = self.client.get('{}?set_active={}'.format(reverse(views.admin_rounds), new_round_id))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 3)
            self.assertEqual(mail.outbox[0].subject, '[nmk] New round "Final2" available')
        rounds = self._get_all_rounds()
        self.assertFalse(rounds[0].active)
        self.assertFalse(rounds[1].active)
        self.assertTrue(rounds[2].active)
        self.assertTrue(rounds[3].active)

    def test_round_set_inactive(self):
        response = self.client.post(reverse(views.admin_rounds_edit), {'name': 'Final2', 'group_type': 'Cup'})
        self.assertEqual(response.status_code, 302)
        rounds = self._get_all_rounds()
        new_round_id = rounds[3].id

        response = self.client.get('{}?set_active={}'.format(reverse(views.admin_rounds), new_round_id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('{}?set_inactive={}'.format(reverse(views.admin_rounds), 3))
        self.assertEqual(response.status_code, 200)

        rounds = self._get_all_rounds()
        for nmk_round in rounds:
            self.assertEqual(nmk_round.active, nmk_round.id == new_round_id)
