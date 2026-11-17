from functools import wraps
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import Event, Department, Faculty, Approval, User, AuditLog, ApprovalHistory
from app.extensions import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Administrator privileges are required to access this console.', 'danger')
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_active_event():
    event = Event.query.filter_by(is_active=True).first()
    if not event:
        event = Event.query.first()
    return event

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    event = get_active_event()
    total_departments = Department.query.count()
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_coordinators = User.query.filter_by(role='coordinator').count()
    total_approved = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    recent_approvals = Approval.query.order_by(Approval.approval_time.desc()).limit(8).all()

    return render_template(
        'admin/admin_dashboard.html',
        event=event,
        total_departments=total_departments,
        total_faculty=total_faculty,
        total_coordinators=total_coordinators,
        total_approved=total_approved,
        recent_approvals=recent_approvals
    )

@admin_bp.route('/event-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def event_settings():
    event = get_active_event()
    if request.method == 'POST':
        event.title = request.form.get('title', event.title).strip()
        event.college_short_name = request.form.get('college_short_name', event.college_short_name).strip()
        event.college_name = request.form.get('college_name', event.college_name).strip()
        event.tagline = request.form.get('tagline', event.tagline).strip()
        event.supporting_message = request.form.get('supporting_message', event.supporting_message).strip()
        event.invitation_text = request.form.get('invitation_text', event.invitation_text).strip()
        event.event_date = request.form.get('event_date', event.event_date).strip()
        event.event_time = request.form.get('event_time', event.event_time).strip()
        event.venue = request.form.get('venue', event.venue).strip()
        event.organizer_details = request.form.get('organizer_details', event.organizer_details).strip()

        log = AuditLog(
            user_id=current_user.id,
            action='event_updated',
            target_model='Event',
            target_id=event.id,
            details=f"Updated event configuration: {event.title}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash('Event configurations updated successfully.', 'success')
        return redirect(url_for('admin.event_settings'))

    return render_template('admin/event_settings.html', event=event)

@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    departments_list = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', departments=departments_list)

@admin_bp.route('/departments/add', methods=['POST'])
@login_required
@admin_required
def add_department():
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    speciality = request.form.get('speciality', '').strip()
    quote = request.form.get('quote', '').strip()
    hod_name = request.form.get('hod_name', '').strip()
    icon_name = request.form.get('icon_name', 'cpu').strip()
    theme_color = request.form.get('theme_color', '#C6A15B').strip()

    if not name or not code:
        flash('Department name and code are mandatory.', 'danger')
        return redirect(url_for('admin.departments'))

    existing = Department.query.filter((Department.name == name) | (Department.code == code)).first()
    if existing:
        flash(f'A department with name "{name}" or code "{code}" already exists.', 'warning')
        return redirect(url_for('admin.departments'))

    dept = Department(
        name=name,
        code=code,
        speciality=speciality,
        quote=quote,
        hod_name=hod_name,
        icon_name=icon_name,
        theme_color=theme_color
    )
    db.session.add(dept)
    db.session.flush()

    log = AuditLog(
        user_id=current_user.id,
        action='department_created',
        target_model='Department',
        target_id=dept.id,
        details=f"Created department: {dept.name} ({dept.code})",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Department "{name}" created successfully.', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/delete/<int:department_id>', methods=['POST'])
@login_required
@admin_required
def delete_department(department_id):
    dept = Department.query.get_or_404(department_id)
    name = dept.name
    db.session.delete(dept)

    log = AuditLog(
        user_id=current_user.id,
        action='department_deleted',
        target_model='Department',
        target_id=department_id,
        details=f"Deleted department: {name}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Department "{name}" removed.', 'info')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/faculty')
@login_required
@admin_required
def faculty():
    event = get_active_event()
    departments_list = Department.query.order_by(Department.name).all()
    faculty_list = Faculty.query.filter_by(is_active=True).order_by(Faculty.name).all()
    return render_template('admin/faculty.html', faculties=faculty_list, departments=departments_list, event=event)

@admin_bp.route('/faculty/add', methods=['POST'])
@login_required
@admin_required
def add_faculty():
    name = request.form.get('name', '').strip()
    salutation = request.form.get('salutation', 'Prof.').strip()
    department_id = request.form.get('department_id')
    designation = request.form.get('designation', 'Assistant Professor').strip()
    cabin_number = request.form.get('cabin_number', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if not name or not department_id:
        flash('Faculty name and department are required.', 'danger')
        return redirect(url_for('admin.faculty'))

    fac = Faculty(
        name=name,
        salutation=salutation,
        department_id=int(department_id),
        designation=designation,
        cabin_number=cabin_number,
        email=email,
        phone=phone
    )
    db.session.add(fac)
    db.session.flush()

    log = AuditLog(
        user_id=current_user.id,
        action='faculty_added',
        target_model='Faculty',
        target_id=fac.id,
        details=f"Added faculty member {fac.full_display_name} to department #{department_id}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Faculty {fac.full_display_name} enrolled successfully.', 'success')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/delete/<int:faculty_id>', methods=['POST'])
@login_required
@admin_required
def delete_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)
    fac.is_active = False  # soft delete

    log = AuditLog(
        user_id=current_user.id,
        action='faculty_deactivated',
        target_model='Faculty',
        target_id=fac.id,
        details=f"Deactivated faculty {fac.full_display_name}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Faculty {fac.full_display_name} deactivated.', 'info')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/coordinators')
@login_required
@admin_required
def coordinators():
    coord_list = User.query.order_by(User.role, User.full_name).all()
    return render_template('admin/coordinators.html', coordinators=coord_list)

@admin_bp.route('/coordinators/add', methods=['POST'])
@login_required
@admin_required
def add_coordinator():
    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('username', '').strip().lower()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    role = request.form.get('role', 'coordinator')

    if not full_name or not username or not password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.coordinators'))

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username or email already registered.', 'warning')
        return redirect(url_for('admin.coordinators'))

    user = User(
        full_name=full_name,
        username=username,
        email=email,
        role=role,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    log = AuditLog(
        user_id=current_user.id,
        action='coordinator_created',
        target_model='User',
        target_id=user.id,
        details=f"Created {role} account: @{username} ({full_name})",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Account for {full_name} created.', 'success')
    return redirect(url_for('admin.coordinators'))

@admin_bp.route('/coordinators/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_coordinator(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot deactivate primary administrator.', 'danger')
        return redirect(url_for('admin.coordinators'))

    user.is_active = not user.is_active
    status = 'activated' if user.is_active else 'deactivated'

    log = AuditLog(
        user_id=current_user.id,
        action=f'coordinator_{status}',
        target_model='User',
        target_id=user.id,
        details=f"{status.capitalize()} user @{user.username}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Account for {user.full_name} has been {status}.', 'info')
    return redirect(url_for('admin.coordinators'))

@admin_bp.route('/approvals')
@login_required
@admin_required
def approvals():
    approvals_list = Approval.query.order_by(Approval.approval_time.desc()).all()
    return render_template('admin/approvals_list.html', approvals=approvals_list)

@admin_bp.route('/approvals/reset/<int:approval_id>', methods=['POST'])
@login_required
@admin_required
def reset_approval(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    reason = request.form.get('reason', 'Reset by Administrator').strip()

    approval.status = 'reset'

    hist = ApprovalHistory(
        approval_id=approval.id,
        action='reset',
        performed_by_id=current_user.id,
        reason=reason
    )
    log = AuditLog(
        user_id=current_user.id,
        action='approval_reset',
        target_model='Approval',
        target_id=approval.id,
        details=f"Reset approval for {approval.faculty.full_display_name}. Reason: {reason}",
        ip_address=request.remote_addr
    )
    db.session.add_all([hist, log])
    db.session.commit()
    flash(f'Approval for {approval.faculty.full_display_name} has been reset.', 'warning')
    return redirect(url_for('approvals.approval_details', approval_id=approval.id))

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(150).all()
    return render_template('admin/audit_logs.html', logs=logs)

