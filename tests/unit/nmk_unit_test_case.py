# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from django.urls import reverse

from nmkapp import logic, views, cache, models


class NmkUnitTestCase(TestCase):
    fixtures = ['initial_data.json']

    def __init__(self, *args, **kwargs):
        super(NmkUnitTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.assertTrue(self.client.login(username='kokan@mail.com', password='12345'))

        # Recalculate all points in DB (we don't trust fixtures to contain properly calculated points)
        logic.recalculate_round_points(1)
        logic.recalculate_round_points(2)
        logic.recalculate_round_points(3)
        logic.recalculate_total_points()

        # Clear cache
        groups = models.Group.objects.all()
        rounds = models.Round.objects.all()
        for group in groups:
            cache.StandingsCache(group).clear()
        cache.StandingsCache().clear()
        for nmk_round in rounds:
            cache.RoundStandingsCache.clear_round(nmk_round)

    def _get_all_rounds(self):
        response = self.client.get(reverse(views.admin_rounds))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertTrue('rounds' in context)
        self.assertIsNotNone(context['rounds'])
        return context['rounds']
