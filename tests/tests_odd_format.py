# -*- coding: utf-8 -*-

from django.test import TestCase

from nmkapp.logic import convert_odd_format
from nmkapp.models import Player


class OddFormatTests(TestCase):
    def test_decimal_format(self):
        self.assertEqual('', convert_odd_format(None, Player.DECIMAL))
        self.assertEqual('', convert_odd_format('', Player.DECIMAL))
        self.assertEqual('1', convert_odd_format('1', Player.DECIMAL))
        self.assertEqual('1', convert_odd_format(1, Player.DECIMAL))
        self.assertEqual('1.0', convert_odd_format(1.0, Player.DECIMAL))
        self.assertEqual('2.5', convert_odd_format(2.5, Player.DECIMAL))
        self.assertEqual('0.4', convert_odd_format(0.4, Player.DECIMAL))
        self.assertEqual('-2.3', convert_odd_format(-2.3, Player.DECIMAL))

    def test_uk_format_invalid_input(self):
        self.assertEqual(None, convert_odd_format(None, Player.FRACTIONAL))
        self.assertRaises(TypeError, convert_odd_format, '')
        self.assertRaises(TypeError, convert_odd_format, 'text')
        self.assertRaises(TypeError, convert_odd_format, [1, 2, 3])
        self.assertEqual('N/A', convert_odd_format(0, Player.FRACTIONAL))
        self.assertEqual('N/A', convert_odd_format(-1, Player.FRACTIONAL))
        self.assertEqual('N/A', convert_odd_format(-2.5, Player.FRACTIONAL))

    def test_uk_format(self):
        self.assertEqual('0/1', convert_odd_format(1, Player.FRACTIONAL))
        self.assertEqual('0/1', convert_odd_format(1.0, Player.FRACTIONAL))
        self.assertEqual('1/-2', convert_odd_format(0.5, Player.FRACTIONAL))
        self.assertEqual('1/2', convert_odd_format(1.5, Player.FRACTIONAL))
        self.assertEqual('1/1', convert_odd_format(2, Player.FRACTIONAL))
        self.assertEqual('7/2', convert_odd_format(4.5, Player.FRACTIONAL))
        self.assertEqual('19/1', convert_odd_format(20.0, Player.FRACTIONAL))
        self.assertEqual('49/1', convert_odd_format(50, Player.FRACTIONAL))
        self.assertEqual('37/100', convert_odd_format(1.37, Player.FRACTIONAL))
        self.assertEqual('37/100', convert_odd_format(1.37112, Player.FRACTIONAL))
        self.assertEqual('371/1000', convert_odd_format(1.37112, Player.FRACTIONAL, precision=3))
        self.assertEqual('3711/10000', convert_odd_format(1.37112, Player.FRACTIONAL, precision=4))
        self.assertEqual('101/200', convert_odd_format(1.505, Player.FRACTIONAL, precision=3))
        self.assertEqual('101/200', convert_odd_format(1.505, Player.FRACTIONAL, precision=4))

    def test_unknown_format(self):
        self.assertEqual('', convert_odd_format(None, Player.DECIMAL))
        self.assertEqual('', convert_odd_format('', 100))
        self.assertEqual('1', convert_odd_format('1', 100))
        self.assertEqual(1, convert_odd_format(1, 100))
        self.assertEqual(1, convert_odd_format(1.0, 100))
        self.assertEqual(2.5, convert_odd_format(2.5, 100))
        self.assertEqual(0.4, convert_odd_format(0.4, 100))
        self.assertEqual(-2.3, convert_odd_format(-2.3, 100))
