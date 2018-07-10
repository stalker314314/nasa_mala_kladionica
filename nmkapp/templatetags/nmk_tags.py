# -*- coding: utf-8 -*-

from django import template

from nmkapp.logic import convert_odd_format

register = template.Library()


@register.filter
def odd_format(value, odd_format_type):
    return convert_odd_format(value, odd_format_type)
