from sqlalchemy import null
from app import create_app, db
from app.models import User, Lecturer, Student, Seminar, Supervision, Honorarium
import datetime

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Makes additional variables available in the Flask shell context."""
    return {
        'db': db, 'User': User, 'Lecturer': Lecturer, 
        'Student': Student, 'Seminar': Seminar, 'Supervision': Supervision,
        'Honorarium': Honorarium
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
            
            db.session.add_all([dosen1, dosen2, dosen3, dosen4])

            # --- Create Student Users ---
            # Student 1: At Seminar Hasil stage (has passed Seminar Proposal)
            mhs1_step = 1
            user_mhs1 = User(sso_email='melan.rena@student.ut.ac.id', role='mahasiswa')
            user_mhs1.set_password('password123')
            mahasiswa1 = Student(user=user_mhs1, nim='501203182', name='MELAN RENA', research_title='MENAVIGASI BADAI PASAR SAHAM', status_bimbingan=progress_steps[mhs1_step], masa='20242', program_studi='MM', ut_daerah='Jakarta', current_progress_step=mhs1_step, zoom_link='https://sl.ut.ac.id/BTRIMKeuangan12112024')

            # Student 2: At Tahapan 1 stage
            mhs2_step = 1
            user_mhs2 = User(sso_email='dicky.yudha@student.ut.ac.id', role='mahasiswa')
            user_mhs2.set_password('password123')
            mahasiswa2 = Student(user=user_mhs2, nim='501253234', name='DICKY YUDHA PERDANA', status_bimbingan=progress_steps[mhs2_step], masa='20242', program_studi='MM', ut_daerah='Bandung', current_progress_step=mhs2_step)

            # Student 3: At Sidang Tertutup stage (has passed Sempro & Semhas)
            mhs3_step = 1
            user_mhs3 = User(sso_email='gebian.ridho@student.ut.ac.id', role='mahasiswa')
            user_mhs3.set_password('password123')
            mahasiswa3 = Student(user=user_mhs3, nim='501273229', name='GEBIAN RIDHO SADEWA', research_title='Pengaruh Pelatihan Karyawan', status_bimbingan=progress_steps[mhs3_step], masa='20251', program_studi='MM', ut_daerah='Yogyakarta', current_progress_step=mhs3_step, zoom_link='https://sl.ut.ac.id/BTRIMSDSMPemasar283582021')
            
            db.session.add_all([mahasiswa1, mahasiswa2, mahasiswa3])
            db.session.commit()

            # --- Create Supervision Relationships ---
            sup1 = Supervision(lecturer_id=dosen2.id, student_id=mahasiswa1.id, role='Promotor')
            sup2 = Supervision(lecturer_id=dosen1.id, student_id=mahasiswa1.id, role='Ko-Promotor 1')
            sup_mhs1_copro2 = Supervision(lecturer_id=dosen4.id, student_id=mahasiswa1.id, role='Ko-Promotor 2')
            sup5 = Supervision(lecturer_id=dosen3.id, student_id=mahasiswa3.id, role='Promotor')
            
            # Tambahkan sup_mhs1_copro2 ke session
            db.session.add_all([sup1, sup2, sup_mhs1_copro2, sup5])

            # # --- Create Seminar Data According to Student Stages ---
            # # Student 1 (passed sempro, now at semhas)
            # seminar_mhs1_proposal = Seminar(student_id=mahasiswa1.id, seminar_type='Seminar Proposal', date=datetime.date(2024, 11, 12))
            # seminar_mhs1_hasil = Seminar(student_id=mahasiswa1.id, seminar_type='Seminar Hasil', date=datetime.date(2025, 3, 15))
            # seminar_mhs2_proposal = Seminar(student_id=mahasiswa2.id, seminar_type='Seminar Proposal', date=datetime.date(2025, 4, 10))
            # seminar_mhs3_proposal = Seminar(student_id=mahasiswa3.id, seminar_type='Seminar Proposal', date=datetime.date(2025, 4, 16))
            # seminar_mhs3_hasil = Seminar(student_id=mahasiswa3.id, seminar_type='Seminar Hasil', date=datetime.date(2025, 6, 20))
            # seminar_mhs3_sidang_tutup = Seminar(student_id=mahasiswa3.id, seminar_type='Sidang Tertutup', date=datetime.date(2025, 7, 25))
            
            # # Data untuk Sidang Komisi (tanpa nilai awal)
            # sidang_pra_proposal = Seminar(student_id=mahasiswa2.id, seminar_type='Sidang Komisi Pra-Proposal', date=datetime.date(2025, 4, 1))
            # sidang_pra_semhas = Seminar(student_id=mahasiswa1.id, seminar_type='Sidang Komisi Pra-Seminar Hasil', date=datetime.date(2025, 3, 1))
            # sidang_pra_tertutup = Seminar(student_id=mahasiswa3.id, seminar_type='Sidang Komisi Pra-Ujian Tertutup', date=datetime.date(2025, 7, 15))

            # db.session.add_all([
            #     seminar_mhs1_proposal, seminar_mhs1_hasil,
            #     seminar_mhs2_proposal,
            #     seminar_mhs3_proposal, seminar_mhs3_hasil, seminar_mhs3_sidang_tutup,
            #     sidang_pra_proposal, sidang_pra_semhas, sidang_pra_tertutup
            # ])
            
            db.session.commit()
            print("Database has been successfully populated with new initial data.")

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)
