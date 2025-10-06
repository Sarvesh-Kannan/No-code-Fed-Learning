import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_bHR7VTgl5eKv@ep-broad-brook-a13kxylc-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MODEL_FOLDER = './models'
    VISUALIZATION_FOLDER = './static/visualizations'
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAUsSQuwbnlOxyj7kXCF8AgaIYi36H5X0g')
    
    # JWT
    JWT_EXPIRATION_HOURS = 24

