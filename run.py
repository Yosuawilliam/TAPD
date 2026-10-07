from sqlalchemy import null
from app import create_app, db
from app.models import User, Lecturer, Student, Seminar, Supervision, Honorarium, Admin
import datetime

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Makes additional variables available in the Flask shell context."""
    return {
        'db': db, 'User': User, 'Lecturer': Lecturer, 
        'Student': Student, 'Seminar': Seminar, 'Supervision': Supervision,
        'Honorarium': Honorarium, 'Admin': Admin
    }

def setup_database(app_instance):
    """Initializes the database with sample data aligned with the 14-stage progress."""
    with app_instance.app_context():
        # db.drop_all() # Deletes all old data to ensure a clean slate
        db.create_all()

        if User.query.first() is None:
            print("Creating initial users and data...")

            # Define status names according to the 14 progress stages
            progress_steps = {
                1: "Bimbingan Tahap 1", 
                2: "Sidang Komisi Pra-Seminar Proposal", 
                3: "Sidang Seminar Proposal",
                4: "Bimbingan Tahap 2", 
                5: "Sidang Komisi Pra-Seminar Hasil", 
                6: "Sidang Seminar Hasil",
                7: "Bimbingan Tahap 3", 
                8: "Sidang Komisi Pra-Ujian Tertutup",
                9: "Sidang Tertutup", 
                10: "Perbaikan Sidang", 
                11: "Sidang Terbuka (Promosi)",
                12: "Revisi Final", 
                13: "Yudisium",
                14: "Proses Kelulusan"
            }

            # --- Create Admin User ---
            user_admin = User(sso_email='admin@ut.ac.id', role='admin')
            user_admin.set_password('password123')
            admin_data = Admin(user=user_admin, name='Administrator UT')
            db.session.add_all([user_admin, admin_data])
            
            # --- Create Lecturer Users ---
            user_dosen1 = User(sso_email='andi.harmoko@ut.ac.id', role='dosen')
            user_dosen1.set_password('password123')
            dosen1 = Lecturer(user=user_dosen1, name='DR. ANDI HARMOKO ARIFIN, S.E., M.SI', nip='198604162022031001')

            user_dosen2 = User(sso_email='faizul.mubarok@ut.ac.id', role='dosen')
            user_dosen2.set_password('password123')
            dosen2 = Lecturer(user=user_dosen2, name='DR. FAIZUL MUBAROK, M.M.', nip='198501012021011001')

            user_dosen3 = User(sso_email='tubaggus@ut.ac.id', role='dosen')
            user_dosen3.set_password('password123')
            dosen3 = Lecturer(user=user_dosen3, name='PROF. DR. TUBAGGUS, MM, AK, CA, CPA', nip='198501012021023001')

            user_dosen4 = User(sso_email='irwati@ut.ac.id', role='dosen')
            user_dosen4.set_password('password123')
            dosen4 = Lecturer(user=user_dosen4, name='DR. IRWATI, HM, S.E., M.SI', nip='198501012021011004')
            
            db.session.commit()
            print("Database initial users (Admin & Lecturers) initialized.")

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)
