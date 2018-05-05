print*
import os
import sys
sys.stdout = sys.stderr

path = '/sites/'
if path not in sys.path:
        sys.path.append(path)

path = '/sites/sharkz.bet/'
if path not in sys.path:
        sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nmk.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
