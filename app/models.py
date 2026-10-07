from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sso_email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50), nullable=False)
    
    lecturer = db.relationship('Lecturer', backref='user', uselist=False, cascade="all, delete-orphan")
    student = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    admin = db.relationship('Admin', backref='user', uselist=False, cascade="all, delete-orphan") # Relasi Admin
    
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# --- MODEL ADMIN BARU ---
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    nip = db.Column(db.String(50), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    supervisions = db.relationship('Supervision', back_populates='lecturer', foreign_keys='Supervision.lecturer_id')
    applications_received = db.relationship('SupervisorApplication', backref='lecturer', lazy='dynamic')
    profile_picture = db.Column(db.String(100), nullable=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    nim = db.Column(db.String(20), unique=True, nullable=False, index=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    research_title = db.Column(db.String(500))
    status_bimbingan = db.Column(db.String(100))
    masa = db.Column(db.String(20))
    program_studi = db.Column(db.String(100))
    ut_daerah = db.Column(db.String(100))
    current_progress_step = db.Column(db.Integer, default=1)
    zoom_link = db.Column(db.String(255))
    supervisions = db.relationship('Supervision', back_populates='student', foreign_keys='Supervision.student_id')
    seminars = db.relationship('Seminar', backref='student_profile', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='student_profile', lazy='dynamic')
    applications_sent = db.relationship('SupervisorApplication', backref='student', lazy='dynamic')
    def get_supervisor_by_role(self, role_name):
        supervision = next((s for s in self.supervisions if s.role == role_name), None)
        return supervision.lecturer if supervision else None

class Supervision(db.Model):
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    lecturer = db.relationship('Lecturer', back_populates='supervisions', foreign_keys=[lecturer_id])
    student = db.relationship('Student', back_populates='supervisions', foreign_keys=[student_id])

class Seminar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    seminar_type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    final_grade = db.Column(db.String(10), nullable=True)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey('seminar.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    evaluation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    final_grade = db.Column(db.String(10), nullable=True) 
    general_notes = db.Column(db.Text, nullable=True) 
    criteria_scores = db.Column(db.JSON, nullable=True)
    seminar = db.relationship('Seminar', backref=db.backref('evaluations', lazy='dynamic'))

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    progress_step = db.Column(db.Integer, nullable=False)
    student = db.relationship('Student', backref=db.backref('documents', lazy='dynamic'))
    uploader = db.relationship('User')
    approvals = db.relationship('DocumentApproval', backref='document', lazy='dynamic', cascade="all, delete-orphan")

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    attachment_filename = db.Column(db.String(255), nullable=True)
    student = db.relationship('Student', backref=db.backref('chat_messages', lazy='dynamic'))
    sender = db.relationship('User')

class Bimbingan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    proposed_date = db.Column(db.Date, nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    student = db.relationship('Student', backref=db.backref('bimbingan_requests', lazy='dynamic'))
    lecturer = db.relationship('Lecturer', backref=db.backref('bimbingan_requests', lazy='dynamic'))

class Honorarium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    lecturer = db.relationship('Lecturer', backref='honorariums')
    student = db.relationship('Student', backref='honorariums')

class DocumentApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=True) 
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class SupervisorApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    role_applied_for = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    research_title_applied = db.Column(db.String(500), nullable=True)