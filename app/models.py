import uuid
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

# Association table for Coordinator <-> Department many-to-many relationship
coordinator_departments = db.Table(
    'coordinator_departments',
    db.Column('coordinator_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='coordinator')  # 'admin' or 'coordinator'
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    assigned_departments = db.relationship('Department', secondary=coordinator_departments, backref=db.backref('assigned_coordinators', lazy='dynamic'))
    approvals_collected = db.relationship('Approval', backref='coordinator', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, default='SANSKRITI 2026')
    subtitle = db.Column(db.String(255), default='Digital Freshers Invitation & Faculty Blessings Experience')
    tagline = db.Column(db.String(255), default='New Beginnings, Beautiful Connections, Endless Memories.')
    supporting_message = db.Column(db.Text, default="Every new journey deserves a beautiful welcome. Let's celebrate new friendships, new dreams and the beginning of an unforgettable college journey.")
    invitation_text = db.Column(db.Text, default="With immense pleasure and joy, we invite our respected faculty members to join us in welcoming the new members of our college family. Let's make this beginning memorable!")
    college_name = db.Column(db.String(200), default='Shri Balaji Institute of Technology & Management')
    college_short_name = db.Column(db.String(50), default='SBITM')
    college_logo = db.Column(db.String(255), default='/static/images/logo/sanskriti_logo.svg')
    event_date = db.Column(db.String(100), default='November 28, 2026')
    event_time = db.Column(db.String(100), default='10:00 AM onwards')
    venue = db.Column(db.String(200), default='Grand Central Auditorium & Campus Lawns')
    organizer_details = db.Column(db.String(255), default='Student Council & Cultural Affairs Committee')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    approvals = db.relationship('Approval', backref='event', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.title}>'


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    speciality = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quote = db.Column(db.Text, nullable=False)
    hod_name = db.Column(db.String(120), nullable=True)
    icon_name = db.Column(db.String(50), default='cpu')  # Lucide icon name
    theme_color = db.Column(db.String(20), default='#C6A15B')
    banner_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    faculties = db.relationship('Faculty', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    approvals = db.relationship('Approval', backref='department', lazy='dynamic')

    def approved_count(self, event_id=None):
        query = Approval.query.filter_by(department_id=self.id, status='approved')
        if event_id:
            query = query.filter_by(event_id=event_id)
        return query.count()

    def total_faculty_count(self):
        return self.faculties.filter_by(is_active=True).count()

    def approval_status(self, event_id=None):
        total = self.total_faculty_count()
        if total == 0:
            return 'empty'
        approved = self.approved_count(event_id)
        if approved >= total:
            return 'approved'
        elif approved > 0:
            return 'in_progress'
        return 'pending'

    def __repr__(self):
        return f'<Department {self.code}: {self.name}>'


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    salutation = db.Column(db.String(20), default='Prof.')
    designation = db.Column(db.String(100), default='Assistant Professor')
    cabin_number = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    approvals = db.relationship('Approval', backref='faculty', lazy='dynamic')

    @property
    def full_display_name(self):
        if self.salutation and not self.name.startswith(self.salutation):
            return f"{self.salutation} {self.name}"
        return self.name

    def has_approved(self, event_id=None):
        query = Approval.query.filter_by(faculty_id=self.id, status='approved')
        if event_id:
            query = query.filter_by(event_id=event_id)
        return query.first() is not None

    def get_approval(self, event_id=None):
        query = Approval.query.filter_by(faculty_id=self.id, status='approved')
        if event_id:
            query = query.filter_by(event_id=event_id)
        return query.first()

    def __repr__(self):
        return f'<Faculty {self.full_display_name}>'


class Approval(db.Model):
    __tablename__ = 'approvals'

    id = db.Column(db.Integer, primary_key=True)
    approval_uuid = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='approved')  # 'approved', 'reset', 'rejected'
    approval_time = db.Column(db.DateTime, default=utc_now)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # 1-to-1 relationships
    signature = db.relationship('FacultySignature', backref='approval', uselist=False, cascade='all, delete-orphan')
    selfie = db.relationship('FacultySelfie', backref='approval', uselist=False, cascade='all, delete-orphan')
    message = db.relationship('FacultyMessage', backref='approval', uselist=False, cascade='all, delete-orphan')
    consent = db.relationship('ConsentRecord', backref='approval', uselist=False, cascade='all, delete-orphan')
    history = db.relationship('ApprovalHistory', backref='approval', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Approval {self.approval_uuid} - Faculty {self.faculty_id}>'


class FacultySignature(db.Model):
    __tablename__ = 'faculty_signatures'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approvals.id', ondelete='CASCADE'), unique=True, nullable=False)
    signature_filename = db.Column(db.String(255), nullable=False)
    signature_base64 = db.Column(db.Text, nullable=True)  # In-database persistence for serverless/Vercel
    created_at = db.Column(db.DateTime, default=utc_now)


class FacultySelfie(db.Model):
    __tablename__ = 'faculty_selfies'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approvals.id', ondelete='CASCADE'), unique=True, nullable=False)
    selfie_filename = db.Column(db.String(255), nullable=False)
    selfie_base64 = db.Column(db.Text, nullable=True)  # In-database persistence for serverless/Vercel
    capture_method = db.Column(db.String(30), default='live_camera')  # 'live_camera' or 'manual_upload'
    created_at = db.Column(db.DateTime, default=utc_now)


class FacultyMessage(db.Model):
    __tablename__ = 'faculty_messages'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approvals.id', ondelete='CASCADE'), unique=True, nullable=False)
    message_text = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=True)  # Public display consent
    created_at = db.Column(db.DateTime, default=utc_now)


class ConsentRecord(db.Model):
    __tablename__ = 'consent_records'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approvals.id', ondelete='CASCADE'), unique=True, nullable=False)
    invitation_accepted = db.Column(db.Boolean, default=True)
    signature_consented = db.Column(db.Boolean, default=True)
    selfie_consented = db.Column(db.Boolean, default=True)
    public_display_consented = db.Column(db.Boolean, default=True)
    consent_statement = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now)


class ApprovalHistory(db.Model):
    __tablename__ = 'approval_histories'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approvals.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'submitted', 'reset', 'updated'
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now)

    performed_by = db.relationship('User')


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_model = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now)
