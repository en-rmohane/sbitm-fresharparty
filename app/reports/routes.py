import io
import csv
from datetime import datetime
from flask import render_template, send_file, Response, url_for
from app.reports import reports_bp
from app.models import Event, Department, Faculty, Approval
from app.reports.pdf_generator import (
    generate_invitation_pdf,
    generate_event_approval_report_pdf,
    generate_faculty_blessings_pdf,
    generate_faculty_card_pdf,
    generate_final_summary_pdf
)

def get_active_event():
    event = Event.query.filter_by(is_active=True).first()
    if not event:
        event = Event.query.first()
    return event

@reports_bp.route('/')
def index():
    event = get_active_event()
    return render_template('reports/index.html', event=event)

@reports_bp.route('/download/invitation-pdf')
def download_event_invitation_pdf():
    event = get_active_event()
    pdf_bytes = generate_invitation_pdf(event)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{event.college_short_name}_Sanskriti_2026_Invitation.pdf"
    )

@reports_bp.route('/download/event-report-pdf')
def download_event_report_pdf():
    event = get_active_event()
    approvals = Approval.query.filter_by(event_id=event.id, status='approved').order_by(Approval.approval_time.asc()).all()
    pdf_bytes = generate_event_approval_report_pdf(event, approvals)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Sanskriti_2026_Complete_Approval_Dossier.pdf"
    )

@reports_bp.route('/download/blessings-pdf')
def download_blessings_pdf():
    event = get_active_event()
    approvals = Approval.query.filter_by(event_id=event.id, status='approved').order_by(Approval.approval_time.asc()).all()
    pdf_bytes = generate_faculty_blessings_pdf(event, approvals)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Sanskriti_2026_Faculty_Blessings_Anthology.pdf"
    )

@reports_bp.route('/download/faculty-card-pdf/<int:approval_id>')
def download_faculty_card_pdf(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    verify_url = url_for('approvals.verify_approval', approval_uuid=approval.approval_uuid, _external=True)
    pdf_bytes = generate_faculty_card_pdf(approval, verify_url)
    clean_name = approval.faculty.name.replace(' ', '_')
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Blessing_Receipt_{clean_name}_{approval.approval_uuid[:8]}.pdf"
    )

@reports_bp.route('/download/final-summary-pdf')
def download_final_summary_pdf():
    event = get_active_event()
    departments = Department.query.order_by(Department.name).all()
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_approved = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    pdf_bytes = generate_final_summary_pdf(event, departments, total_faculty, total_approved)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Sanskriti_2026_Executive_Summary.pdf"
    )

@reports_bp.route('/export/faculty-csv')
def export_faculty_csv():
    event = get_active_event()
    faculties = Faculty.query.filter_by(is_active=True).order_by(Faculty.department_id, Faculty.name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Faculty ID', 'Salutation', 'Full Name', 'Department Code', 'Department Name',
        'Designation', 'Cabin / Room', 'Email', 'Phone', 'Approval Status'
    ])

    for f in faculties:
        has_approved = "Approved" if f.has_approved(event.id if event else None) else "Pending"
        writer.writerow([
            f.id,
            f.salutation,
            f.name,
            f.department.code,
            f.department.name,
            f.designation,
            f.cabin_number or '',
            f.email or '',
            f.phone or '',
            has_approved
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=Sanskriti_2026_Faculty_Directory_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

