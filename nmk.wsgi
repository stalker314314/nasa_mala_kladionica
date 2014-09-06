import os
import sys
sys.stdout = sys.stderr

path = '/sajtovi/'
if path not in sys.path:
        sys.path.append(path)

path = '/sajtovi/nmk.kokanovic.org/'
if path not in sys.path:
        sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nmk.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()