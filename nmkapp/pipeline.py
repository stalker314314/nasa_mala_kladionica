# -*- coding: utf-8 -*-

from social_core.pipeline.partial import partial
from django.urls import reverse
from django.shortcuts import redirect


# Pauses PSA's pipeline to require display_name for users registering
# via 3rd-party(Google, Twitter, etc.)
#
# Returns redirect to a view that requires display_name from user
# or None if display_name is already set(which subsequently continues the pipeline)
@partial
def request_display_name(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.first_name:
        return
    else:
        return redirect(reverse('request_display_name'))
