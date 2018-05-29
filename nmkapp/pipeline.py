from social_core.pipeline.partial import partial
from django.shortcuts import redirect
# from nmkapp.views import request_password

@partial
def request_display_name(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.first_name:
        return
    else:
        return redirect('request_display_name')
