import os

from falcon_core.wsgi import get_wsgi_application

os.environ.setdefault('FALCON_CORE_SETTINGS_MODULE', 'gusto_api.settings')

application = get_wsgi_application()
