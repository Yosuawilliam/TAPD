from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User, Lecturer, Student
from urllib.parse import urlsplit

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'dosen':
            return redirect(url_for('main.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('main.kelola_panduan'))
        else:
            return redirect(url_for('student.dashboard'))
    
    login_form = LoginForm()
    reg_form = RegistrationForm() 

    if login_form.validate_on_submit():
        user = User.query.filter_by(sso_email=login_form.sso_email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Email atau password tidak valid', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=login_form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            if user.role == 'dosen':
                next_page = url_for('main.dashboard')
            elif user.role == 'admin':
                next_page = url_for('main.kelola_panduan')
            else:
                next_page = url_for('student.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Login', login_form=login_form, reg_form=reg_form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register/dosen', methods=['GET', 'POST'])
def register_dosen():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    login_form = LoginForm()
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        user = User(sso_email=reg_form.sso_email.data, role='dosen')
        user.set_password(reg_form.password.data)
        lecturer = Lecturer(
            user=user, 
            name=reg_form.name.data, 
            nip=reg_form.id_number.data,
            phone_number=reg_form.phone_number.data
        )
        db.session.add(user)
        db.session.add(lecturer)
        db.session.commit()
        flash('Selamat, akun dosen Anda berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html', title='Daftar Dosen', login_form=login_form, reg_form=reg_form, form_type='register_dosen')

@bp.route('/register/mahasiswa', methods=['GET', 'POST'])
def register_mahasiswa():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
        
    login_form = LoginForm()
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        if not reg_form.ut_daerah.data:
             flash('Silakan pilih UT Daerah asal Anda.', 'danger')
             return render_template('auth/login.html', title='Daftar Mahasiswa', login_form=login_form, reg_form=reg_form, form_type='register_mahasiswa')

        user = User(sso_email=reg_form.sso_email.data, role='mahasiswa')
        user.set_password(reg_form.password.data)
        student = Student(
            user=user, 
            name=reg_form.name.data, 
            nim=reg_form.id_number.data,
            phone_number=reg_form.phone_number.data,
            ut_daerah=reg_form.ut_daerah.data, 
            status_bimbingan="Bimbingan Tahap 1", 
            current_progress_step=1
        )
        db.session.add(user)
        db.session.add(student)
        db.session.commit()
        flash('Selamat, akun mahasiswa Anda berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html', title='Daftar Mahasiswa', login_form=login_form, reg_form=reg_form, form_type='register_mahasiswa')