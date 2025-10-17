import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Connection string for the PostgreSQL database
    DATABASE_URL = os.getenv("DATABASE_URL")