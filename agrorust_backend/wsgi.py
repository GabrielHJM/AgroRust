import os
from django.core.handlers.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrorust_backend.settings')
application = get_wsgi_application()
