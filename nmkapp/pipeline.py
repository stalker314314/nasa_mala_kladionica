from social_core.pipeline.partial import partial
from django.shortcuts import redirect
# from nmkapp.views import request_password

@partial
def request_password(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.password:
        print('return')
        from pprint import pprint
        pprint(vars(user))
        return
    elif is_new:
        print(is_new)
        print(user.password)
        is_new = False
        return redirect('request_password')


def test(strategy, details, user=None, is_new=False, *args, **kwargs):
    print ('zavrseno')
