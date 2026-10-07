import os
import shutil

# Get the absolute path of the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class. Contains default settings that can be
    inherited and overridden by other configuration classes.
    """
    # Secret key is used for session management and security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'

    # Database configuration
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    elif os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        db_path = os.path.join('/tmp', 'app.db')
        src_db = os.path.join(basedir, 'app.db')
        if os.path.exists(src_db) and not os.path.exists(db_path):
            try:
                shutil.copy2(src_db, db_path)
            except Exception as e:
                print(f"Failed to copy DB to /tmp: {e}")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
    else:
        UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

