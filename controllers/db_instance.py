from models.database import Database
from config import Config

# singleton DB instance used across the app to avoid circular imports
db = Database(Config.DATABASE_URL)
db.connect()