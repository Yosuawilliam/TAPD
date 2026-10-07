from flask import Blueprint

# 1. Definisikan blueprint terlebih dahulu
bp = Blueprint('auth', __name__)

# 2. Impor rute di bagian bawah SETELAH blueprint didefinisikan.
# Ini akan memutus siklus impor.
from app.auth import routes