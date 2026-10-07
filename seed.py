from app import create_app, db
from app.models import User, Lecturer, Student, Supervision, Admin, Seminar, Evaluation
import datetime

app = create_app()

def seed_data():
    with app.app_context():
        # Drop all & recreate for fresh clean seed if needed, or check User
        print("[+] Memulai proses injeksi data awal (Seeding)...")
        db.drop_all()
        db.create_all()

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
        print(" - (Tidak ada data mahasiswa awal)")
        print("\n PASSWORD UNTUK SEMUA AKUN: password123")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_data()