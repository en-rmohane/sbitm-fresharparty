from flask import render_template, current_app
from app.departments import departments_bp
from app.models import Event, Department, Faculty, Approval

def get_active_event():
    event = Event.query.filter_by(is_active=True).first()
    if not event:
        event = Event.query.first()
    return event

@departments_bp.route('/')
def landing():
    event = get_active_event()
    return render_template('landing.html', event=event)

@departments_bp.route('/invitation')
def invitation():
    event = get_active_event()
    return render_template('invitation.html', event=event)

@departments_bp.route('/departments')
def department_universe():
    event = get_active_event()
    departments = Department.query.order_by(Department.name).all()
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_approved = Approval.query.filter_by(event_id=event.id, status='approved').count() if event else 0
    return render_template(
        'department_universe.html',
        event=event,
        departments=departments,
        total_faculty=total_faculty,
        total_approved=total_approved
    )

