import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:23456@postgresql:5432/geodb')
COOKIE_SECRET_KEY = os.environ.get('COOKIE_SECRET_KEY', 'В ПРОДАКШЕН ЗАДАТЬ СЛУЧАЙНУЮ СТРОКУ')