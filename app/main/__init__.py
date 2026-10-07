from flask import Blueprint

bp = Blueprint('main', __name__)

# Impor rute di bagian bawah untuk menghindari circular import
from app.main import routes