"""
WSGI config for utm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'utm.settings')

application = get_wsgi_application()

# Ensure database tables and default roles exist automatically in ephemeral environments (e.g. Render)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('setup_roles')
except Exception as _mig_err:
    print(f"[UTM WSGI] Automatic initialization notice: {_mig_err}")
