import os
import io
import re
import uuid
import base64
import qrcode
from datetime import datetime, timezone
from flask import render_template, request, jsonify, url_for, redirect, flash, send_file, current_app, abort
from flask_login import login_required, current_user
from app.approvals import approvals_bp
from app.models import (
    Event, Department, Faculty, Approval, FacultySignature,
    FacultySelfie, FacultyMessage, ConsentRecord, ApprovalHistory, AuditLog
)
from app.extensions import db

def get_active_event():
    event = Event.query.filter_by(is_active=True).first()
    if not event:
        event = Event.query.first()
    return event

def save_base64_image(base64_str, folder, default_ext='png'):
    """Decodes a base64 image data URL and saves it securely with a random filename.
    Gracefully handles serverless read-only filesystems."""
    filename = f"{uuid.uuid4().hex}.{default_ext}"
    try:
        os.makedirs(folder, exist_ok=True)
        # Match data URL pattern e.g. data:image/png;base64,xxxx
        match = re.match(r'^data:image/(\w+);base64,(.+)$', base64_str)
        if match:
            ext = match.group(1).lower()
            if ext == 'jpeg':
                ext = 'jpg'
            data = base64.b64decode(match.group(2))
        else:
            # Raw base64 string
            ext = default_ext
            data = base64.b64decode(base64_str)

        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
    except Exception as e:
        current_app.logger.warning(f"Could not persist image to disk (likely serverless): {e}")

    return filename

@approvals_bp.route('/api/submit', methods=['POST'])
@login_required
def api_submit_approval():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload received.'}), 400

        faculty_id = data.get('faculty_id')
        event_id = data.get('event_id')
        department_id = data.get('department_id')
        signature_base64 = data.get('signature_base64')
        selfie_base64 = data.get('selfie_base64')
        capture_method = data.get('capture_method', 'live_camera')
        message_text = (data.get('message_text') or '').strip()
        is_public = bool(data.get('is_public', True))

        if not faculty_id or not signature_base64 or not selfie_base64:
            return jsonify({'success': False, 'message': 'Missing required fields: faculty, signature, or selfie.'}), 400

        faculty = db.session.get(Faculty, faculty_id)
        if not faculty:
            return jsonify({'success': False, 'message': 'Faculty member not found.'}), 404

        # Check for existing active approval to prevent duplicate submissions
        existing = Approval.query.filter_by(
            faculty_id=faculty_id,
            event_id=event_id,
            status='approved'
        ).first()

        if existing:
            return jsonify({
                'success': True,
                'message': 'Approval already exists.',
                'redirect_url': url_for('approvals.approval_details', approval_id=existing.id)
            })

        # Save signature image
        sig_folder = current_app.config['SIGNATURE_FOLDER']
        sig_filename = save_base64_image(signature_base64, sig_folder, 'png')

        # Save selfie image
        selfie_folder = current_app.config['SELFIE_FOLDER']
        selfie_filename = save_base64_image(selfie_base64, selfie_folder, 'jpg')

        # Create master Approval record
        approval = Approval(
            approval_uuid=str(uuid.uuid4()),
            event_id=event_id,
            department_id=department_id or faculty.department_id,
            faculty_id=faculty_id,
            coordinator_id=current_user.id,
            status='approved',
            approval_time=datetime.now(timezone.utc),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else 'Unknown'
        )
        db.session.add(approval)
        db.session.flush()

        # Create 1-to-1 detail records with base64 data persistence for Vercel / serverless
        signature_record = FacultySignature(
            approval_id=approval.id,
            signature_filename=sig_filename,
            signature_base64=signature_base64
        )
        selfie_record = FacultySelfie(
            approval_id=approval.id,
            selfie_filename=selfie_filename,
            selfie_base64=selfie_base64,
            capture_method=capture_method
        )
        message_record = FacultyMessage(
            approval_id=approval.id,
            message_text=message_text,
            is_public=is_public
        )
        consent_record = ConsentRecord(
            approval_id=approval.id,
            invitation_accepted=True,
            signature_consented=True,
            selfie_consented=True,
            public_display_consented=is_public,
            consent_statement="Consent given to coordinator in person during Sanskriti 2026 digital invitation visit."
        )
        history_record = ApprovalHistory(
            approval_id=approval.id,
            action='submitted',
            performed_by_id=current_user.id,
            reason='Initial physical campus collection'
        )
        audit_log = AuditLog(
            user_id=current_user.id,
            action='approval_collected',
            target_model='Approval',
            target_id=approval.id,
            details=f"Collected blessing from {faculty.full_display_name} ({faculty.department.code})",
            ip_address=request.remote_addr
        )

        db.session.add_all([signature_record, selfie_record, message_record, consent_record, history_record, audit_log])
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Blessing recorded successfully!',
            'approval_uuid': approval.approval_uuid,
            'redirect_url': url_for('approvals.approval_success', approval_uuid=approval.approval_uuid)
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting approval: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Server error processing approval: {str(e)}'}), 500

@approvals_bp.route('/success/<approval_uuid>')
def approval_success(approval_uuid):
    approval = Approval.query.filter_by(approval_uuid=approval_uuid).first_or_404()
    return render_template('approvals/approval_success.html', approval=approval)

@approvals_bp.route('/<int:approval_id>')
@login_required
def approval_details(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    return render_template('approvals/approval_details.html', approval=approval)

@approvals_bp.route('/verify/<approval_uuid>')
def verify_approval(approval_uuid):
    approval = Approval.query.filter_by(approval_uuid=approval_uuid, status='approved').first_or_404()
    return render_template('approvals/verify.html', approval=approval)

@approvals_bp.route('/qr/<approval_uuid>')
def approval_qr_image(approval_uuid):
    # Generates a QR Code in PNG format linking to the verification URL
    verify_url = url_for('approvals.verify_approval', approval_uuid=approval_uuid, _external=True)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#641E28", back_color="#FFF8EB")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@approvals_bp.route('/blessings-wall')
def blessings_wall():
    event = get_active_event()
    departments = Department.query.order_by(Department.name).all()

    # Query approvals for active event with status approved
    query = Approval.query.filter_by(status='approved')
    if event:
        query = query.filter_by(event_id=event.id)

    # If user is not authenticated, only show public consent records on the public wall
    if not current_user.is_authenticated:
        query = query.join(ConsentRecord).filter(ConsentRecord.public_display_consented == True)

    approved_records = query.order_by(Approval.approval_time.desc()).all()

    return render_template(
        'approvals/faculty_memory_wall.html',
        event=event,
        departments=departments,
        approved_records=approved_records
    )

@approvals_bp.route('/journey')
def approval_journey():
    # Hidden from public access per user request
    return redirect(url_for('departments.landing'))

@approvals_bp.route('/dashboard')
def live_dashboard():
    # Hidden from public access per user request
    return redirect(url_for('departments.landing'))

@approvals_bp.route('/api/stats')
def api_stats():
    event = get_active_event()
    departments = Department.query.order_by(Department.name).all()
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    approved_count = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    pending_count = max(0, total_faculty - approved_count)
    completion_pct = round((approved_count / total_faculty * 100), 1) if total_faculty > 0 else 0

    dept_stats = []
    for d in departments:
        dept_stats.append({
            'id': d.id,
            'name': d.name,
            'code': d.code,
            'approved': d.approved_count(event.id if event else None),
            'total': d.total_faculty_count(),
            'status': d.approval_status(event.id if event else None)
        })

    return jsonify({
        'total_departments': len(departments),
        'total_faculty': total_faculty,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'completion_percentage': completion_pct,
        'departments': dept_stats
    })

@approvals_bp.route('/grand-finale')
def grand_finale():
    event = get_active_event()
    departments = Department.query.order_by(Department.name).all()
    total_departments = len(departments)
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_approved = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    pending_count = max(0, total_faculty - total_approved)
    completion_pct = round((total_approved / total_faculty * 100), 1) if total_faculty > 0 else 0

    is_completed = (total_faculty > 0 and total_approved >= total_faculty)

    return render_template(
        'approvals/grand_finale.html',
        event=event,
        departments=departments,
        total_departments=total_departments,
        total_faculty=total_faculty,
        total_approved=total_approved,
        pending_count=pending_count,
        completion_pct=completion_pct,
        is_completed=is_completed
    )

# Secure File Serving Handlers (supports both file disk & in-database base64 for Vercel)
@approvals_bp.route('/file/signature/<int:approval_id>')
def view_signature(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    if not approval.signature:
        abort(404)

    # 1. Try serving from disk
    filepath = os.path.join(current_app.config['SIGNATURE_FOLDER'], approval.signature.signature_filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')

    # 2. Serverless fallback: Serve directly from database base64
    if approval.signature.signature_base64:
        match = re.match(r'^data:image/(\w+);base64,(.+)$', approval.signature.signature_base64)
        raw_b64 = match.group(2) if match else approval.signature.signature_base64
        return send_file(io.BytesIO(base64.b64decode(raw_b64)), mimetype='image/png')

    abort(404)

@approvals_bp.route('/file/selfie/<int:approval_id>')
def view_selfie(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    if not approval.selfie:
        abort(404)

    # Privacy verification: allowed if public consent given, or if user is logged in
    is_public = approval.consent and approval.consent.public_display_consented
    if not is_public and not current_user.is_authenticated:
        abort(403)

    # 1. Try serving from disk
    filepath = os.path.join(current_app.config['SELFIE_FOLDER'], approval.selfie.selfie_filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/jpeg')

    # 2. Serverless fallback: Serve directly from database base64
    if approval.selfie.selfie_base64:
        match = re.match(r'^data:image/(\w+);base64,(.+)$', approval.selfie.selfie_base64)
        raw_b64 = match.group(2) if match else approval.selfie.selfie_base64
        return send_file(io.BytesIO(base64.b64decode(raw_b64)), mimetype='image/jpeg')

    abort(404)
