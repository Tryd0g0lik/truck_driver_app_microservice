import asyncio

from project.db.corn import create_db, Settings

# SQLAlchemy create db's table
settings = Settings()
asyncio.run(create_db(settings))
