from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.coordinator import coordinator_bp
from app.models import Event, Department, Faculty, Approval

def get_active_event():
    event = Event.query.filter_by(is_active=True).first()
    if not event:
        event = Event.query.first()
    return event

@coordinator_bp.route('/dashboard')
@login_required
def dashboard():
    event = get_active_event()
    assigned_departments = current_user.assigned_departments
    if not assigned_departments:
        # If no specific departments assigned, allow all departments
        assigned_departments = Department.query.order_by(Department.name).all()

    my_approvals_count = Approval.query.filter_by(coordinator_id=current_user.id, status='approved').count()
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_approved = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    total_pending = max(0, total_faculty - total_approved)
    overall_completion_pct = round((total_approved / total_faculty * 100), 1) if total_faculty > 0 else 0

    recent_approvals = Approval.query.filter_by(
        coordinator_id=current_user.id, status='approved'
    ).order_by(Approval.approval_time.desc()).limit(10).all()

    return render_template(
        'coordinator/dashboard.html',
        event=event,
        assigned_departments=assigned_departments,
        my_approvals_count=my_approvals_count,
        total_faculty=total_faculty,
        total_approved=total_approved,
        total_pending=total_pending,
        overall_completion_pct=overall_completion_pct,
        recent_approvals=recent_approvals
    )

@coordinator_bp.route('/department/<int:department_id>')
@login_required
def faculty_selection(department_id):
    event = get_active_event()
    department = Department.query.get_or_404(department_id)
    faculties = Faculty.query.filter_by(department_id=department.id, is_active=True).order_by(Faculty.name).all()
    approved_count = department.approved_count(event.id if event else None)
    total_count = len(faculties)

    return render_template(
        'coordinator/faculty_selection.html',
        event=event,
        department=department,
        faculties=faculties,
        approved_count=approved_count,
        total_count=total_count
    )

@coordinator_bp.route('/faculty/<int:faculty_id>/approval')
@login_required
def approval_wizard(faculty_id):
    event = get_active_event()
    faculty = Faculty.query.get_or_404(faculty_id)

    # Check if faculty already has an active approval for this event
    existing_approval = Approval.query.filter_by(
        faculty_id=faculty.id,
        event_id=event.id if event else 1,
        status='approved'
    ).first()

    if existing_approval:
        flash(f'{faculty.full_display_name} has already recorded their blessing!', 'info')
        return redirect(url_for('approvals.approval_details', approval_id=existing_approval.id))

    return render_template(
        'approvals/approval_wizard.html',
        event=event,
        faculty=faculty
    )

