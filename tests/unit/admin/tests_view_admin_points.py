# -*- coding: utf-8 -*-

from django.test import Client
from django.urls import reverse

from nmkapp import views, models

from ..nmk_unit_test_case import NmkUnitTestCase


class AdminPointsTests(NmkUnitTestCase):
    def test_anon_user(self):
        client = Client()
        response = client.get(reverse(views.admin_points))
        self.assertEqual(response.status_code, 302)

    def test_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username='seki', password='12345'))
        response = client.get(reverse(views.admin_points))
        self.assertEqual(response.status_code, 302)

    def test_stuff_user_lands(self):
        response = self.client.get(reverse(views.admin_points))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])

    def test_recalculate_all(self):
        player = models.Player.objects.filter(user__id=1).get()
        old_points = player.points
        player.points = 0
        player.save()
        response = self.client.post(reverse(views.admin_points),
                                    {'recalculate_points': True, 'clear_cache': True, 'repopulate_cache': True})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIsNotNone(context['form'])
        player = models.Player.objects.filter(user__id=1).get()
        self.assertEqual(old_points, player.points)
