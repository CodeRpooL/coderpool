import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

project_home = BASE_DIR
if project_home not in sys.path:
    sys.path.append(project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
