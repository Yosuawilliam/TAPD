from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField, IntegerField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email, NumberRange, EqualTo, Optional, Length

from app.models import User

# Daftar UT Daerah
UT_DAERAH_CHOICES = [
    ('', 'Pilih UT Daerah'),
    ('Ambon', 'Ambon'), ('Banda Aceh', 'Banda Aceh'), ('Bandar Lampung', 'Bandar Lampung'),
    ('Bandung', 'Bandung'), ('Banjarmasin', 'Banjarmasin'), ('Batam', 'Batam'),
    ('Bengkulu', 'Bengkulu'), ('Bogor', 'Bogor'), ('Denpasar', 'Denpasar'),
    ('Gorontalo', 'Gorontalo'), ('Jakarta', 'Jakarta'), ('Jambi', 'Jambi'),
    ('Jayapura', 'Jayapura'), ('Jember', 'Jember'), ('Kendari', 'Kendari'),
    ('Kupang', 'Kupang'), ('Luar Negeri', 'Luar Negeri'), ('Majene', 'Majene'),
    ('Makassar', 'Makassar'), ('Malang', 'Malang'), ('Manado', 'Manado'),
    ('Mataram', 'Mataram'), ('Medan', 'Medan'), ('Padang', 'Padang'),
    ('Palangkaraya', 'Palangkaraya'), ('Palembang', 'Palembang'), ('Palu', 'Palu'),
    ('Pangkal Pinang', 'Pangkal Pinang'), ('Pekanbaru', 'Pekanbaru'), ('Pontianak', 'Pontianak'),
    ('Purwokerto', 'Purwokerto'), ('Samarinda', 'Samarinda'), ('Semarang', 'Semarang'),
    ('Serang', 'Serang'), ('Sorong', 'Sorong'), ('Surabaya', 'Surabaya'),
    ('Surakarta', 'Surakarta'), ('Tarakan', 'Tarakan'), ('Ternate', 'Ternate'),
    ('Yogyakarta', 'Yogyakarta')
]

class LoginForm(FlaskForm):
    sso_email = StringField('SSO Akun', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Ingat saya')
    submit = SubmitField('Masuk')

class EvaluationCriteriaForm(FlaskForm):
    score = IntegerField('Score', validators=[NumberRange(min=0, max=100)])
    adequate = RadioField('Adequate', choices=[('ya', 'Ya'), ('tidak', 'Tidak')])
    feedback = TextAreaField('Feedback')

class RegistrationForm(FlaskForm):
    sso_email = StringField('Email SSO', validators=[DataRequired(), Email()])
    name = StringField('Nama Lengkap', validators=[DataRequired()])
    id_number = StringField('NIP / NIM', validators=[DataRequired()])
    
    # Kolom Nomor HP ditambahkan
    phone_number = StringField('Nomor Telepon / WA', validators=[DataRequired(), Length(min=10, max=15)])
    
    ut_daerah = SelectField('UT Daerah', choices=UT_DAERAH_CHOICES, validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Ulangi Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar')

    def validate_sso_email(self, sso_email):
        user = User.query.filter_by(sso_email=sso_email.data).first()
        if user is not None:
            raise ValidationError('Email ini sudah terdaftar. Silakan gunakan email lain.')