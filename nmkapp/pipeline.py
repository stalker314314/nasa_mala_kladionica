# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from social_core.backends.google import GoogleOAuth2
from social_core.pipeline.partial import partial


@partial
def request_display_name(strategy, details, user=None, is_new=False, *args, **kwargs):
    """
    Pauses PSA's pipeline to require display_name for users registering via 3rd-party(Google, Twitter, etc.)

    Returns redirect to a view that requires display_name from user
    or None if display_name is already set (which subsequently continues the pipeline)
    """
    if user and user.first_name:
        return
    else:
        return redirect('request_display_name')


def fill_username_with_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if isinstance(strategy.request.backend, GoogleOAuth2):
        user.username = user.email
        user.save()
    return
