from social_core.pipeline.partial import partial
from django.shortcuts import redirect

@partial
def request_display_name(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.first_name:
        return
    else:
        return redirect('request_display_name')
