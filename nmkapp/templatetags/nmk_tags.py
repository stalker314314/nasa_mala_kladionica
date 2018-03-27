import datetime 
from django import template

register = template.Library()

@register.simple_tag(takes_context=False)
def is_registration_allowed():
    last_registration_time = datetime.datetime(2018, 6, 14, 16, 0)
    return datetime.datetime.now() < last_registration_time