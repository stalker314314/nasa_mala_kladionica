# -*- coding: utf-8 -*-

from django.db import connection, connections, DEFAULT_DB_ALIAS
from django.urls import reverse
from django.test import TransactionTestCase, Client
from django.test.utils import CaptureQueriesContext


from nmkapp import logic, views, cache, models


class NmkUnitTestCase(TransactionTestCase):
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

    def assertNumQueriesLessThan(self, num, func=None, *args, using=DEFAULT_DB_ALIAS, **kwargs):
        conn = connections[using]

        context = _AssertNumQueriesContext(self, num, conn)
        if func is None:
            return context

        with context:
            func(*args, **kwargs)

#changed assertEqual to assertLess
class _AssertNumQueriesContext(CaptureQueriesContext):
    def __init__(self, test_case, num, connection):
        self.test_case = test_case
        self.num = num
        super().__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return
        executed = len(self)
        self.test_case.assertLess(
            executed, self.num,
            "%d queries executed, %d expected\nCaptured queries were:\n%s" % (
                executed, self.num,
                '\n'.join(
                    '%d. %s' % (i, query['sql']) for i, query in enumerate(self.captured_queries, start=1)
                )
            )
        )
