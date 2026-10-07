from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Buat objek metadata dengan konvensi penamaan
metadata = MetaData(naming_convention=convention)

# Inisialisasi ekstensi dengan metadata
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Silakan login untuk mengakses halaman ini.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.add_extension('jinja2.ext.do')
    db.init_app(app)
    # Aktifkan 'render_as_batch' untuk dukungan alter table di SQLite
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)

    try:
        import os
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        print(f"Could not create upload directory: {e}")

    # Daftarkan semua blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.student import bp as student_bp
    app.register_blueprint(student_bp)

    return app

from app import models