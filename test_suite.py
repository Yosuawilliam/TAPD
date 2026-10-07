import unittest
import json
import os
import datetime
from app import create_app, db
from app.models import User, Lecturer, Student, Seminar, Supervision, Evaluation, Admin

class UniversityAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.drop_all()
            db.create_all()
            cls._seed_test_data()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    @classmethod
    def _seed_test_data(cls):
        # Create Dosen
        user_dosen = User(sso_email='test.dosen@ut.ac.id', role='dosen')
        user_dosen.set_password('password123')
        dosen = Lecturer(user=user_dosen, name='DR. TEST DOSEN, M.M.', nip='198501012021019999')
        db.session.add_all([user_dosen, dosen])
        db.session.commit()

        # Create Mahasiswa
        user_mhs = User(sso_email='test.student@student.ut.ac.id', role='mahasiswa')
        user_mhs.set_password('password123')
        student = Student(
            user=user_mhs,
            nim='999999999',
            name='MAHASISWA TEST',
            research_title='ANALISIS SISTEM INFORMASI AKADEMIK',
            status_bimbingan='Sidang Seminar Proposal',
            masa='20242',
            program_studi='MM',
            ut_daerah='Jakarta',
            current_progress_step=3
        )
        db.session.add_all([user_mhs, student])
        db.session.commit()

        # Create Supervision
        sup = Supervision(lecturer_id=dosen.id, student_id=student.id, role='Promotor')
        db.session.add(sup)
        db.session.commit()

        # Create Seminar
        seminar1 = Seminar(
            student_id=student.id,
            seminar_type='Sidang Komisi Pra-Seminar Proposal',
            date=datetime.date(2024, 11, 12)
        )
        seminar2 = Seminar(
            student_id=student.id,
            seminar_type='Sidang Komisi Pra-Seminar Hasil',
            date=datetime.date(2025, 3, 15)
        )
        db.session.add_all([seminar1, seminar2])
        db.session.commit()

        # Add initial evaluation for seminar1
        eval1 = Evaluation(
            seminar_id=seminar1.id,
            student_id=student.id,
            evaluator_id=dosen.id,
            final_grade='A',
            general_notes='Sangat Baik',
            criteria_scores={'pendahuluan': 90, 'metodologi': 88}
        )
        db.session.add(eval1)
        db.session.commit()

        cls.dosen_user_id = user_dosen.id
        cls.student_id = student.id
        cls.seminar1_id = seminar1.id
        cls.seminar2_id = seminar2.id

    def login_dosen(self):
        return self.client.post('/auth/login', data={
            'sso_email': 'test.dosen@ut.ac.id',
            'password': 'password123'
        }, follow_redirects=True)

    def test_01_login_dosen(self):
        response = self.login_dosen()
        self.assertEqual(response.status_code, 200)
        print(" [PASS] Test 1: Login Dosen Berhasil (/auth/login)")

    def test_02_get_student_seminars_api(self):
        self.login_dosen()
        response = self.client.get(f'/api/student/{self.student_id}/seminars')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['type'], 'Sidang Komisi Pra-Seminar Proposal')
        print(f" [PASS] Test 2: API /api/student/{self.student_id}/seminars mengembalikan {len(data)} data seminar")

    def test_03_masukan_hasil_seminar_page(self):
        self.login_dosen()
        response = self.client.get('/masukan_hasil_seminar')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MAHASISWA TEST', response.data)
        self.assertIn(b'Sidang Komisi Pra-Seminar Proposal', response.data)
        print(" [PASS] Test 3: Halaman Masukan Hasil Seminar berhasil menampilkan riwayat seminar mahasiswa")

    def test_04_submit_seminar_grade(self):
        self.login_dosen()
        payload = {
            'seminar_id': self.seminar2_id,
            'final_grade': 'A-',
            'general_notes': 'Presentasi cukup baik, perjelas analisis data.',
            'criteria_scores': {'pendahuluan': 85, 'pembahasan': 87}
        }
        response = self.client.post('/submit_seminar_grade', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.data)
        self.assertEqual(res_data['status'], 'success')
        
        with self.app.app_context():
            seminar = db.session.get(Seminar, self.seminar2_id)
            self.assertEqual(seminar.final_grade, 'A-')
        print(" [PASS] Test 4: Input Nilai Seminar berhasil disimpan ke database")

    def test_05_export_evaluations_excel(self):
        self.login_dosen()
        payload = {'seminar_ids': [self.seminar1_id, self.seminar2_id]}
        response = self.client.post('/export-evaluations', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(len(response.data) > 0)
        print(" [PASS] Test 5: Export Rekapitulasi Nilai ke Excel (.xlsx) Berhasil Generated")

    def test_06_document_approval_creates_seminar(self):
        from app.models import Document, Student, Supervision
        self.login_dosen()
        with self.app.app_context():
            # Create a student at step 1
            u = User(sso_email='student.step1@ut.ac.id', role='mahasiswa')
            u.set_password('pass123')
            s1 = Student(user=u, nim='111222333', name='MHS STEP 1', current_progress_step=1)
            db.session.add_all([u, s1])
            db.session.commit()
            sup = Supervision(lecturer_id=1, student_id=s1.id, role='Promotor')
            db.session.add(sup)
            db.session.commit()

            # Create documents for step 1 required tasks
            doc1 = Document(student_id=s1.id, uploader_id=self.dosen_user_id, document_type='Upload Proposal TAPD', filename='prop.pdf', progress_step=1)
            doc2 = Document(student_id=s1.id, uploader_id=self.dosen_user_id, document_type='Dokumen SK', filename='sk.pdf', progress_step=1)
            doc3 = Document(student_id=s1.id, uploader_id=self.dosen_user_id, document_type='Persetujuan Tim Promotor', filename='acc.pdf', progress_step=1)
            db.session.add_all([doc1, doc2, doc3])
            db.session.commit()
            
            # Approve doc1 & doc2
            self.client.post('/approve_document', data=json.dumps({'document_id': doc1.id}), content_type='application/json')
            self.client.post('/approve_document', data=json.dumps({'document_id': doc2.id}), content_type='application/json')
            
            # Approve final doc3 (should trigger progress advance from 1 to 2 -> Sidang Komisi Pra-Seminar Proposal)
            response = self.client.post('/approve_document', data=json.dumps({'document_id': doc3.id}), content_type='application/json')
            res_data = json.loads(response.data)
            self.assertTrue(res_data['advanced_to_next_step'])
            
            # Check if Seminar was created automatically
            seminar = Seminar.query.filter_by(student_id=s1.id, seminar_type='Sidang Komisi Pra-Seminar Proposal').first()
            self.assertIsNotNone(seminar)
        print(" [PASS] Test 6: Persetujuan Dokumen Otomatis Membuat Record Seminar Baru")

    def test_07_all_supervisors_must_approve(self):
        from app.models import Document, Student, Supervision, DocumentApproval
        self.login_dosen()
        with self.app.app_context():
            u = User(sso_email='student.multi_sup@ut.ac.id', role='mahasiswa')
            u.set_password('pass123')
            s2 = Student(user=u, nim='444555666', name='MHS MULTI SUP', current_progress_step=1)
            db.session.add_all([u, s2])
            db.session.commit()
            
            # Add 3 supervisors: lecturer 1, 2, 3
            sup1 = Supervision(lecturer_id=1, student_id=s2.id, role='Promotor')
            sup2 = Supervision(lecturer_id=2, student_id=s2.id, role='Ko-Promotor 1')
            sup3 = Supervision(lecturer_id=3, student_id=s2.id, role='Ko-Promotor 2')
            db.session.add_all([sup1, sup2, sup3])
            db.session.commit()

            doc1 = Document(student_id=s2.id, uploader_id=self.dosen_user_id, document_type='Upload Proposal TAPD', filename='prop.pdf', progress_step=1)
            doc2 = Document(student_id=s2.id, uploader_id=self.dosen_user_id, document_type='Dokumen SK', filename='sk.pdf', progress_step=1)
            doc3 = Document(student_id=s2.id, uploader_id=self.dosen_user_id, document_type='Persetujuan Tim Promotor', filename='acc.pdf', progress_step=1)
            db.session.add_all([doc1, doc2, doc3])
            db.session.commit()

            # Approve all 3 docs only by lecturer 1 (Promotor)
            db.session.add(DocumentApproval(document_id=doc1.id, lecturer_id=1, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc2.id, lecturer_id=1, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc3.id, lecturer_id=1, is_approved=True))
            db.session.commit()

            # Advance check should fail because lecturer 2 and 3 haven't approved
            from app.main.routes import check_and_advance_progress
            advanced_partial = check_and_advance_progress(s2)
            self.assertFalse(advanced_partial)
            self.assertEqual(s2.current_progress_step, 1)

            # Now add approval from lecturer 2 & 3
            db.session.add(DocumentApproval(document_id=doc1.id, lecturer_id=2, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc2.id, lecturer_id=2, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc3.id, lecturer_id=2, is_approved=True))
            
            db.session.add(DocumentApproval(document_id=doc1.id, lecturer_id=3, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc2.id, lecturer_id=3, is_approved=True))
            db.session.add(DocumentApproval(document_id=doc3.id, lecturer_id=3, is_approved=True))
            db.session.commit()

            # Advance check should now succeed
            advanced_full = check_and_advance_progress(s2)
            self.assertTrue(advanced_full)
            self.assertEqual(s2.current_progress_step, 2)
        print(" [PASS] Test 7: Wajib Dihadiri Persetujuan Lengkap (Promotor, Ko-Promotor 1 & 2) Untuk Naik Tahap")

if __name__ == '__main__':
    unittest.main()

