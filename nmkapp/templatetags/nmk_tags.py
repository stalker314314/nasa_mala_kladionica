# -*- coding: utf-8 -*-

import datetime

from django import template
from django.utils import timezone

from nmkapp.logic import convert_odd_format

register = template.Library()


@register.simple_tag(takes_context=False)
def is_registration_allowed():
    last_registration_time = datetime.datetime(2018, 6, 14, 14, 0, tzinfo=timezone.utc)
    return timezone.now() < last_registration_time


@register.filter
def odd_format(value, odd_format_type):
    return convert_odd_format(value, odd_format_type)
