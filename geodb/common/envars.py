import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:23456@postgresql:5432/geodb')