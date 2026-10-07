from flask import flash, redirect, render_template, abort, request, jsonify, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from app.student import bp
from app.models import Evaluation, Lecturer, SupervisorApplication, db, Student, Document, ChatMessage, Bimbingan, Seminar
from werkzeug.utils import secure_filename
import os
import datetime

# --- REVISI TAHAPAN SESUAI 14 STEP ---
tahapan = {}

# Tahap 1: Bimbingan Tahap 1
tahapan[1] = [
    {'type': 'Upload Proposal TAPD', 'icon': 'fa-file-word'},
    {'type': 'Dokumen SK', 'icon': 'fa-file-contract'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 2: Sidang Komisi Pra-Seminar Proposal
tahapan[2] = [
    {'type': 'Draft TAPD (Bab 1-3)', 'icon': 'fa-book'},
    {'type': 'PPT Seminar', 'icon': 'fa-file-powerpoint'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 3: Sidang Seminar Proposal
tahapan[3] = [
    {'type': 'Draft TAPD (Lengkap)', 'icon': 'fa-file-word'},
    {'type': 'PPT Seminar Proposal', 'icon': 'fa-file-powerpoint'},
    {'type': 'Bukti Buku Bimbingan', 'icon': 'fa-book'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 4: Bimbingan Tahap 2
tahapan[4] = [
    {'type': 'Draft TAPD', 'icon': 'fa-file-word'},
    {'type': 'Analisis Data (Data Mentah & Hasil)', 'icon': 'fa-table'},
    {'type': 'PPT TAPD', 'icon': 'fa-file-powerpoint'},
    {'type': 'Bukti Buku Bimbingan', 'icon': 'fa-book'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 5: Sidang Komisi Pra-Seminar Hasil
tahapan[5] = [
    {'type': 'Draft TAPD (Bab 1-5)', 'icon': 'fa-book'},
    {'type': 'Analisis Data (Data Mentah & Hasil)', 'icon': 'fa-table'},
    {'type': 'Letter of Acceptance (LoA)', 'icon': 'fa-envelope-open-text'},
    {'type': 'Sertifikat Conference (Peserta)', 'icon': 'fa-certificate'},
    {'type': 'Sertifikat Conference (Penyaji)', 'icon': 'fa-certificate'},
    {'type': 'Artikel Proceeding', 'icon': 'fa-newspaper'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 6: Sidang Seminar Hasil
tahapan[6] = [
    {'type': 'Draft TAPD (Siap Uji)', 'icon': 'fa-file-word'},
    {'type': 'Publikasi Artikel', 'icon': 'fa-newspaper'},
    {'type': 'PPT Seminar Hasil', 'icon': 'fa-file-powerpoint'},
    {'type': 'Hasil Uji Plagiasi', 'icon': 'fa-search'},
    {'type': 'Bukti Buku Bimbingan', 'icon': 'fa-book'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 7: Bimbingan Tahap 3
tahapan[7] = [
    {'type': 'Draft Perbaikan TAPD', 'icon': 'fa-file-word'},
    {'type': 'PPT TAPD', 'icon': 'fa-file-powerpoint'},
    {'type': 'Bukti Buku Bimbingan', 'icon': 'fa-book'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 8: Sidang Komisi Pra-Ujian Tertutup
tahapan[8] = [
    {'type': 'TAPD Final (Draft Disertasi)', 'icon': 'fa-book'},
    {'type': 'Dokumen Persyaratan Sidang', 'icon': 'fa-folder-open'},
    {'type': 'Persetujuan Tim Promotor', 'icon': 'fa-file-signature'}
]

# Tahap 9: Sidang Tertutup
tahapan[9] = [
    {'type': 'Pertanggung jawaban akademik promotor', 'icon': 'fa-file-contract'},
    {'type': 'CV Mahasiswa', 'icon': 'fa-user-tie'},
    {'type': 'PPT Sidang Tertutup', 'icon': 'fa-file-powerpoint'}
]

# Tahap 10: Perbaikan Sidang
tahapan[10] = [
    {'type': 'Revisi Disertasi (Pasca Tertutup)', 'icon': 'fa-book-open'}
]

# Tahap 11: Sidang Terbuka (Promosi)
tahapan[11] = [
    {'type': 'PPT Sidang Terbuka', 'icon': 'fa-file-powerpoint'}
]

# Tahap 12: Revisi Final
tahapan[12] = [
    {'type': 'Disertasi Final', 'icon': 'fa-book'}
]

# Tahap 13: Yudisium
tahapan[13] = []

# Tahap 14: Proses Kelulusan
tahapan[14] = []

TAHAPAN_TUGAS = tahapan

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'mahasiswa':
        abort(403)
    
    student = current_user.student
    if not student:
        flash('Data mahasiswa tidak ditemukan.', 'danger')
        return redirect(url_for('auth.login'))

    if len(student.supervisions) < 3:
        rejected_applications = student.applications_sent.filter_by(status='Rejected').all()
        for app in rejected_applications:
            flash(f"Pengajuan Anda sebagai {app.role_applied_for} kepada {app.lecturer.name} telah ditolak. Silakan ajukan ke dosen lain.", 'danger')
        flash('Anda harus melengkapi tim pembimbing terlebih dahulu.', 'warning')
        return redirect(url_for('student.ajukan_pembimbing'))

    rejected_applications = student.applications_sent.filter_by(status='Rejected').all()
    required_tasks_info = TAHAPAN_TUGAS.get(student.current_progress_step, [])

    docs_this_step = student.documents.filter_by(progress_step=student.current_progress_step).all()
    uploaded_docs = {doc.document_type: doc for doc in docs_this_step}

    tasks_with_status = []
    for task_info in required_tasks_info:
        doc_type = task_info['type']
        uploaded_document = uploaded_docs.get(doc_type)
        
        approved_by_list = []
        if uploaded_document:
            approvals = uploaded_document.approvals
            for approval in approvals:
                approving_lecturer = Lecturer.query.get(approval.lecturer_id)
                if approving_lecturer:
                    approved_by_list.append(approving_lecturer.name)
        
        task = {
            'type': doc_type,
            'icon': task_info['icon'],
            'uploaded_doc': uploaded_document,
            'approved_by': approved_by_list
        }
        tasks_with_status.append(task)
    
    completed_evaluations = student.evaluations.filter(Evaluation.final_grade.isnot(None)).all()
    bimbingan_requests = Bimbingan.query.filter_by(student_id=student.id).order_by(Bimbingan.created_at.desc()).all()

    # --- DAFTAR 10 TAUTAN PENTING ---
    panduan_dir = os.path.join(current_app.root_path, 'static', 'panduan')
    daftar_tautan = [
        {'nama': 'CARA PEMBAYARAN WISUDA & PANDUAN PEMBUATAN POSTER', 'file': 'Cara_Pembayaran_Wisuda_dan_Pembuatan_Poster.pdf'},
        {'nama': 'DOKUMEN PERLENGKAPAN PENDAFTARAN YUDISIUM', 'file': 'Dokumen_Perlengkapan_Yudisium.pdf'},
        {'nama': 'PAKTA INTEGRITAS PUBLISH PAPER', 'file': 'Pakta_Integritas_Publish_Paper.pdf'},
        {'nama': 'PANDUAN PELAKSANAAN SIDANG TA', 'file': 'Panduan_Pelaksanaan_Sidang.pdf'},
        {'nama': 'PANDUAN PENULISAN PROPOSAL DAN TUGAS AKHIR', 'file': 'Panduan_Proposal_dan_TAPD.pdf'},
        {'nama': 'PANDUAN TUGAS LITERATURE REVIEW PENULISAN PROPOSAL', 'file': 'Panduan_Tugas_Literature_Review.pdf'},
        {'nama': 'RENCANA PEMBELAJARAN SEMESTER MK PENULISAN PROPOSAL', 'file': 'RPS_MK_Penulisan_Proposal.pdf'},
        {'nama': 'RESPONSE FORM', 'file': 'Response_Form.pdf'},
        {'nama': 'SLIDE MATERI MK PENULISAN PROPOSAL', 'file': 'Slide_Materi_MK_Penulisan_Proposal.pdf'},
        {'nama': 'SURAT KETERANGAN INDEX PUBLIKASI DI TTD OLEH PEMBIMBING', 'file': 'Surat_Keterangan_Index_Publikasi.pdf'}
    ]
    
    tautan_tersedia = []
    for tautan in daftar_tautan:
        if os.path.exists(os.path.join(panduan_dir, tautan['file'])):
            tautan_tersedia.append(tautan)

    return render_template('student/dashboard.html', 
                           title='Dashboard Mahasiswa', 
                           student=student,
                           tasks_with_status=tasks_with_status,
                           completed_evaluations=completed_evaluations,
                           bimbingan_requests=bimbingan_requests,
                           rejected_applications=rejected_applications,
                           tautan_tersedia=tautan_tersedia)

@bp.route('/upload_document', methods=['POST'])
@login_required
def upload_document():
    if current_user.role != 'mahasiswa': abort(403)
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Tidak ada file terlampir.'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type')
    
    if file.filename == '' or not document_type:
        return jsonify({'status': 'error', 'message': 'Informasi tidak lengkap.'}), 400

    filename_lower = file.filename.lower()
    
    # --- LOGIKA VALIDASI EKSTENSI FILE BARU ---
    # Dokumen Analisis Data boleh PDF, Excel, CSV
    if "analisis data" in document_type.lower():
        if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.xls') or filename_lower.endswith('.xlsx') or filename_lower.endswith('.csv')):
             return jsonify({'status': 'error', 'message': 'File Analisis Data harus PDF, Excel, atau CSV.'}), 400
    # Draft TAPD boleh Word atau PDF
    elif "draft tapd" in document_type.lower() or "proposal" in document_type.lower():
         if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.doc') or filename_lower.endswith('.docx')):
             return jsonify({'status': 'error', 'message': 'File Draft/Proposal harus PDF atau Word (.doc/.docx).'}), 400
    # Default PDF
    else:
        if not filename_lower.endswith('.pdf'):
            return jsonify({'status': 'error', 'message': 'Hanya file dengan format PDF yang diizinkan untuk dokumen ini.'}), 400

    if file:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        student_nim = current_user.student.nim
        
        # Ambil ekstensi asli file
        ext = filename_lower.split('.')[-1]
        
        base_filename = f"{student_nim}_{document_type.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        final_filename = f"{base_filename}.{ext}"
        filepath = os.path.join(upload_folder, final_filename)
        
        old_doc = Document.query.filter_by(student_id=current_user.student.id, document_type=document_type).first()
        if old_doc:
            try:
                if old_doc.filename and os.path.exists(os.path.join(upload_folder, old_doc.filename)):
                    os.remove(os.path.join(upload_folder, old_doc.filename))
            except OSError as e:
                print(f"Error removing old file: {e}")
            db.session.delete(old_doc)
            db.session.commit()

        file.save(filepath)

        new_doc = Document(
            student_id=current_user.student.id,
            uploader_id=current_user.id,
            document_type=document_type,
            filename=final_filename,
            progress_step=current_user.student.current_progress_step
        )
        db.session.add(new_doc)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'File {document_type} berhasil diunggah.'})
    
    return jsonify({'status': 'error', 'message': 'Gagal mengunggah file.'}), 500

@bp.route('/download/<filename>')
@login_required
def download_document(filename):
    doc = Document.query.filter_by(filename=filename).first_or_404()
    is_owner = current_user.role == 'mahasiswa' and doc.student_id == current_user.student.id
    is_supervisor = (current_user.role == 'dosen' and 
                     any(s.student_id == doc.student_id for s in current_user.lecturer.supervisions))

    if not is_owner and not is_supervisor:
        abort(403)

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@bp.route('/download_chat/<filename>')
@login_required
def download_chat_attachment(filename):
    msg = ChatMessage.query.filter_by(attachment_filename=filename).first_or_404()
    student = msg.student
    is_owner = current_user.role == 'mahasiswa' and student.id == current_user.student.id
    is_supervisor = (current_user.role == 'dosen' and
                     any(s.student_id == student.id for s in current_user.lecturer.supervisions))

    if not is_owner and not is_supervisor:
        abort(403)

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@bp.route('/messages/<int:student_id>')
@login_required
def get_messages(student_id):
    if current_user.role == 'mahasiswa' and current_user.student.id != student_id:
        abort(403)
    elif current_user.role == 'dosen':
        student = Student.query.get_or_404(student_id)
        if not any(s.lecturer_id == current_user.lecturer.id for s in student.supervisions):
            abort(403)

    messages = ChatMessage.query.filter_by(student_id=student_id).order_by(ChatMessage.timestamp.asc()).all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.lecturer.name if msg.sender.role == 'dosen' else msg.sender.student.name,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
            'attachment_filename': msg.attachment_filename 
        })
        
    return jsonify(messages_data)

@bp.route('/send_message/<int:student_id>', methods=['POST'])
@login_required
def send_message(student_id):
    if current_user.role == 'mahasiswa' and current_user.student.id != student_id:
        abort(403)
    elif current_user.role == 'dosen':
        student = Student.query.get_or_404(student_id)
        if not any(s.lecturer_id == current_user.lecturer.id for s in student.supervisions):
            abort(403)

    message_text = request.form.get('message', '')
    file = request.files.get('attachment')
    attachment_filename = None

    if not message_text and not file:
        return jsonify({'status': 'error', 'message': 'Pesan atau file tidak boleh kosong.'}), 400

    if file and file.filename != '':
        student_nim = Student.query.get(student_id).nim
        filename = secure_filename(f"chat_{student_nim}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        attachment_filename = filename

    chat_message = ChatMessage(
        student_id=student_id,
        sender_id=current_user.id,
        message=message_text,
        attachment_filename=attachment_filename
    )
    db.session.add(chat_message)
    db.session.commit()

    new_message_data = {
        'id': chat_message.id,
        'sender_id': chat_message.sender_id,
        'sender_name': chat_message.sender.lecturer.name if chat_message.sender.role == 'dosen' else chat_message.sender.student.name,
        'message': chat_message.message,
        'timestamp': chat_message.timestamp.isoformat(),
        'attachment_filename': chat_message.attachment_filename 
    }

    return jsonify({'status': 'success', 'message_data': new_message_data}), 201

@bp.route('/ajukan-pembimbing', methods=['GET', 'POST'])
@login_required
def ajukan_pembimbing():
    if current_user.role != 'mahasiswa':
        abort(403)
    
    student = current_user.student
    approved_supervisors = {sup.role: sup.lecturer for sup in student.supervisions}
    
    if len(approved_supervisors) >= 3:
        flash('Anda sudah memiliki tim pembimbing yang lengkap.', 'info')
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        role = request.form.get('role')
        lecturer_id = request.form.get('lecturer_id')
        research_title = request.form.get('research_title')

        if not role or not lecturer_id or not research_title:
            flash('Gagal mengirim ajuan. Harap pilih dosen dan pastikan judul sudah terisi.', 'danger')
            return redirect(url_for('student.ajukan_pembimbing'))

        existing_app = SupervisorApplication.query.filter_by(
            student_id=student.id,
            role_applied_for=role,
            status='Pending' 
        ).first()
        if existing_app:
            flash(f'Anda sudah mengajukan pembimbing untuk peran {role}. Harap tunggu persetujuan.', 'warning')
            return redirect(url_for('student.ajukan_pembimbing'))
        
        SupervisorApplication.query.filter_by(student_id=student.id, role_applied_for=role, status='Rejected').delete()
        
        application = SupervisorApplication(
            student_id=student.id,
            lecturer_id=lecturer_id,
            role_applied_for=role,
            research_title_applied=research_title, 
            status='Pending'
        )
        db.session.add(application)
        db.session.commit()
        flash(f'Pengajuan untuk {role} dengan judul penelitian berhasil dikirim.', 'success')
        return redirect(url_for('student.ajukan_pembimbing'))

    lecturers = Lecturer.query.all()
    pending_applications = {app.role_applied_for: app for app in student.applications_sent.filter_by(status='Pending').all()}
    
    return render_template('student/ajukan_pembimbing.html', 
                           title='Ajukan Tim Pembimbing', 
                           lecturers=lecturers,
                           approved_supervisors=approved_supervisors, 
                           pending_applications=pending_applications)

@bp.route('/save_research_title', methods=['POST'])
@login_required
def save_research_title():
    if current_user.role != 'mahasiswa':
        abort(403)
    
    data = request.get_json()
    title = data.get('research_title')

    if not title:
        return jsonify({'status': 'error', 'message': 'Judul tidak boleh kosong.'}), 400

    student = current_user.student
    student.research_title = title
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Judul penelitian berhasil disimpan.'})

@bp.route('/dismiss_rejection/<int:application_id>', methods=['POST'])
@login_required
def dismiss_rejection(application_id):
    if current_user.role != 'mahasiswa':
        abort(403)
        
    app_to_delete = SupervisorApplication.query.get_or_404(application_id)
    
    if app_to_delete.student_id != current_user.student.id:
        abort(403)
        
    db.session.delete(app_to_delete)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Notifikasi telah dihapus.'})

@bp.route('/ajukan-sesi-bimbingan', methods=['POST'])
@login_required
def ajukan_sesi_bimbingan():
    if current_user.role != 'mahasiswa':
        abort(403)

    student_id = current_user.student.id
    lecturer_id = request.form.get('lecturer_id')
    proposed_date_str = request.form.get('proposed_date')
    topic = request.form.get('topic')

    if not all([lecturer_id, proposed_date_str, topic]):
        flash('Semua kolom (Pembimbing, Tanggal, Topik) harus diisi.', 'danger')
        return redirect(url_for('student.dashboard'))

    try:
        proposed_date = datetime.datetime.strptime(proposed_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Format tanggal tidak valid.', 'danger')
        return redirect(url_for('student.dashboard'))

    new_bimbingan = Bimbingan(
        student_id=student_id,
        lecturer_id=lecturer_id,
        proposed_date=proposed_date,
        topic=topic,
        status='Pending'
    )
    db.session.add(new_bimbingan)
    db.session.commit()
    
    flash('Ajuan sesi bimbingan berhasil dikirim.', 'success')
    return redirect(url_for('student.dashboard'))