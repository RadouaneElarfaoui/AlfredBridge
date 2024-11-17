import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Facebook
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    FACEBOOK_VERIFY_TOKEN = os.getenv('FACEBOOK_VERIFY_TOKEN')
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    FACEBOOK_API_VERSION = os.getenv('FACEBOOK_API_VERSION')
    FACEBOOK_DEFAULT_PAGE_ID = os.getenv('FACEBOOK_DEFAULT_PAGE_ID')
    
    # Database
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_HOST = os.getenv('POSTGRES_HOST')
    DB_NAME = os.getenv('POSTGRES_DATABASE')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # App
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_HISTORY_SIZE = int(os.getenv('MAX_HISTORY_SIZE', '100')) 
    
    # Configuration Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')