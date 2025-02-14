# -*- coding: utf-8 -*-
import sys, os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import app as application  # This is the Flask application object
from werkzeug.debug import DebuggedApplication  # Опционально: подключение модуля отладки

# Опционально: включение модуля отадки
application.wsgi_app = DebuggedApplication(application.wsgi_app, True)

# Отключаем режим отладки в production
application.debug = False 

# Optional: Set environment to production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# -*- coding: utf-8 -*-
import sys, os
sys.path.append('/home/u/undercover/getecu/') # указываем директорию с проектом
sys.path.append('/home/d/deniatest/.local/lib/python3.6/site-packages') # указываем директорию с библиотеками, куда поставили Flask
from HelloFlask import app as application # когда Flask стартует, он ищет application. Если не указать 'as application', сайт не заработает
from werkzeug.debug import DebuggedApplication # Опционально: подключение модуля отладки
application.wsgi_app = DebuggedApplication(application.wsgi_app, True) # Опционально: включение модуля отадки
application.debug = False  # Опционально: True/False устанавливается по необходимости в отладке