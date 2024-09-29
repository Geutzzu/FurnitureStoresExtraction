
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MlBackend.settings')

from MlBackend.FurnitureFinder.routing import application

application = application