import os
import dotenv


dotenv.load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# db
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")


# Ip
DATABASE_LOCAL = os.getenv("DATABASE_LOCAL", "")
APP_HOST = os.getenv("APP_HOST", "")
APP_PORT = os.getenv("APP_PORT", "")
DATABASE_ENGINE_REMOTE = os.getenv("DATABASE_ENGINE_REMOTE", "")
