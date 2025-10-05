from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Application settings
APP_NAME = os.getenv('APP_NAME', 'DefaultApp')
APP_ENV = os.getenv('APP_ENV', 'production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Google Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
