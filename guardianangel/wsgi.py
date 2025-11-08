import os
from django.core.wsgi import get_wsgi_application

# Tell Django which settings file to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guardianangel.settings')

# Create the WSGI application object
application = get_wsgi_application()
