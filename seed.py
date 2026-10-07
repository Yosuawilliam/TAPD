from app import create_app, db
from app.models import User, Lecturer, Student, Supervision, Admin

app = create_app()

def seed_data():
    with app.app_context():
        if User.query.first():
            print("[-] Database sudah memiliki data User. Seeding dibatalkan.")
            return

        print("[+] Memulai proses injeksi data awal (Seeding)...")

        progress_steps = {
            1: "Bimbingan Tahap 1", 2: "Sidang Komisi Pra-Seminar Proposal", 
            3: "Sidang Seminar Proposal", 4: "Bimbingan Tahap 2", 
            5: "Sidang Komisi Pra-Seminar Hasil", 6: "Sidang Seminar Hasil",
            7: "Bimbingan Tahap 3", 8: "Sidang Komisi Pra-Ujian Tertutup",
            9: "Sidang Tertutup", 10: "Perbaikan Sidang", 11: "Sidang Terbuka (Promosi)",
            12: "Revisi Final", 13: "Yudisium", 14: "Proses Kelulusan"
        }
        
        # --- Create Admin ---
        user_admin = User(sso_email='admin@ut.ac.id', role='admin')
        user_admin.set_password('password123')
        admin_data = Admin(user=user_admin, name='Administrator UT')
        db.session.add(user_admin)
        db.session.add(admin_data)

        # --- Create Lecturer Users ---
        user_dosen1 = User(sso_email='andi.harmoko@ut.ac.id', role='dosen')
        user_dosen1.set_password('password123')
        dosen1 = Lecturer(user=user_dosen1, name='DR. ANDI HARMOKO ARIFIN, S.E., M.SI', nip='198604162022031001', phone_number='081100000001')

        user_dosen2 = User(sso_email='faizul.mubarok@ut.ac.id', role='dosen')
        user_dosen2.set_password('password123')
        dosen2 = Lecturer(user=user_dosen2, name='DR. FAIZUL MUBAROK, M.M.', nip='198501012021011001', phone_number='081100000002')

        user_dosen3 = User(sso_email='tubaggus@ut.ac.id', role='dosen')
        user_dosen3.set_password('password123')
        dosen3 = Lecturer(user=user_dosen3, name='PROF. DR. TUBAGGUS, MM, AK, CA, CPA', nip='198501012021023001', phone_number='081100000003')

        user_dosen4 = User(sso_email='irwati@ut.ac.id', role='dosen')
        user_dosen4.set_password('password123')
        dosen4 = Lecturer(user=user_dosen4, name='DR. IRWATI, HM, S.E., M.SI', nip='198501012021011004', phone_number='081100000004')
        
        db.session.add_all([user_dosen1, user_dosen2, user_dosen3, user_dosen4])
        db.session.add_all([dosen1, dosen2, dosen3, dosen4])
        db.session.commit()

        # --- Create Student Users ---
        mhs1_step = 1
        user_mhs1 = User(sso_email='melan.rena@student.ut.ac.id', role='mahasiswa')
        user_mhs1.set_password('password123')
        mahasiswa1 = Student(user=user_mhs1, nim='501203182', name='MELAN RENA', research_title='MENAVIGASI BADAI PASAR SAHAM', status_bimbingan=progress_steps[mhs1_step], masa='20242', program_studi='MM', ut_daerah='Jakarta', current_progress_step=mhs1_step, zoom_link='https://sl.ut.ac.id/BTRIMKeuangan12112024', phone_number='081200000001')

        mhs2_step = 1
        user_mhs2 = User(sso_email='dicky.yudha@student.ut.ac.id', role='mahasiswa')
        user_mhs2.set_password('password123')
        mahasiswa2 = Student(user=user_mhs2, nim='501253234', name='DICKY YUDHA PERDANA', status_bimbingan=progress_steps[mhs2_step], masa='20242', program_studi='MM', ut_daerah='Bandung', current_progress_step=mhs2_step, phone_number='081200000002')

        mhs3_step = 1
        user_mhs3 = User(sso_email='gebian.ridho@student.ut.ac.id', role='mahasiswa')
        user_mhs3.set_password('password123')
        mahasiswa3 = Student(user=user_mhs3, nim='501273229', name='GEBIAN RIDHO SADEWA', research_title='Pengaruh Pelatihan Karyawan', status_bimbingan=progress_steps[mhs3_step], masa='20251', program_studi='MM', ut_daerah='Yogyakarta', current_progress_step=mhs3_step, zoom_link='https://sl.ut.ac.id/BTRIMSDSMPemasar283582021', phone_number='081200000003')
        
        db.session.add_all([user_mhs1, user_mhs2, user_mhs3])
        db.session.add_all([mahasiswa1, mahasiswa2, mahasiswa3])
        db.session.commit()

        # --- Create Supervision Relationships ---
        sup1 = Supervision(lecturer_id=dosen2.id, student_id=mahasiswa1.id, role='Promotor')
        sup2 = Supervision(lecturer_id=dosen1.id, student_id=mahasiswa1.id, role='Ko-Promotor 1')
        sup_mhs1_copro2 = Supervision(lecturer_id=dosen4.id, student_id=mahasiswa1.id, role='Ko-Promotor 2')
        sup5 = Supervision(lecturer_id=dosen3.id, student_id=mahasiswa3.id, role='Promotor')
        
        db.session.add_all([sup1, sup2, sup_mhs1_copro2, sup5])
        db.session.commit()
        
        print("\n=======================================================")
        print(" SEEDING DATA AWAL BERHASIL! ")
        print("=======================================================")
        print(" Data Admin:")
        print(" - admin@ut.ac.id")
        print("\n Data Dosen:")
        print(" - andi.harmoko@ut.ac.id")
        print(" - faizul.mubarok@ut.ac.id")
        print(" - tubaggus@ut.ac.id")
        print(" - irwati@ut.ac.id")
        print("\n Data Mahasiswa:")
        print(" - melan.rena@student.ut.ac.id")
        print(" - dicky.yudha@student.ut.ac.id")
        print(" - gebian.ridho@student.ut.ac.id")
        print("\n 🔑 PASSWORD UNTUK SEMUA AKUN: password123")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_data()