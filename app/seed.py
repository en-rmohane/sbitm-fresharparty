import os
import uuid
import io
import base64
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
from app.extensions import db
from app.models import (
    User, Event, Department, Faculty, Approval, FacultySignature,
    FacultySelfie, FacultyMessage, ConsentRecord, ApprovalHistory, AuditLog
)

def create_sample_signature_image(folder, faculty_name):
    filename = f"seed_sig_{uuid.uuid4().hex[:8]}.png"
    img = Image.new('RGBA', (400, 160), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw graceful flowing signature curve strokes
    draw.line([(30, 95), (60, 45), (90, 120), (130, 40), (180, 100), (240, 80), (320, 95)], fill=(58, 16, 25, 230), width=3)
    draw.line([(60, 125), (280, 120)], fill=(198, 161, 91, 180), width=2)
    draw.text((45, 130), faculty_name, fill=(100, 30, 40, 200))

    buf = io.BytesIO()
    img.save(buf, 'PNG')
    b64_str = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

    try:
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(buf.getvalue())
    except Exception:
        pass

    return filename, b64_str

def create_sample_selfie_image(folder, faculty_name):
    filename = f"seed_selfie_{uuid.uuid4().hex[:8]}.jpg"
    img = Image.new('RGB', (480, 480), color=(58, 16, 25))
    draw = ImageDraw.Draw(img)

    # Draw gold border & decorative circles
    draw.rectangle([10, 10, 470, 470], outline=(198, 161, 91), width=4)
    draw.ellipse([140, 100, 340, 300], fill=(100, 30, 40), outline=(223, 186, 115), width=3)
    draw.ellipse([190, 140, 290, 240], fill=(223, 186, 115))

    initials = "".join([part[0] for part in faculty_name.replace('Dr. ', '').replace('Prof. ', '').split()[:2]])
    draw.text((220, 175), initials, fill=(58, 16, 25))
    draw.text((120, 340), faculty_name, fill=(255, 248, 235))
    draw.text((170, 380), "Faculty Blessing", fill=(198, 161, 91))

    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=90)
    b64_str = f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

    try:
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(buf.getvalue())
    except Exception:
        pass

    return filename, b64_str

def seed_database(app):
    with app.app_context():
        # Check if already seeded
        if Event.query.first():
            return

        print("Seeding Sanskriti 2026 database with festive identity and sample data...")

        # 1. Create Default Event
        event = Event(
            title="SANSKRITI 2026",
            subtitle="Digital Freshers Invitation & Faculty Blessings Experience",
            tagline="New Beginnings, Beautiful Connections, Endless Memories.",
            supporting_message="Every new journey deserves a beautiful welcome. Let's celebrate new friendships, new dreams and the beginning of an unforgettable college journey.",
            invitation_text="With immense pleasure and joy, we invite our respected faculty members to join us in welcoming the new members of our college family. Let's make this beginning memorable!",
            college_name="Shri Balaji Institute of Technology & Management",
            college_short_name="SBITM",
            college_logo="/static/images/logo/sanskriti_logo.svg",
            event_date="November 19, 2026",
            event_time="10:00 AM onwards",
            venue="Grand Central Auditorium & Campus Lawns",
            organizer_details="Student Council & Cultural Affairs Committee",
            is_active=True
        )
        db.session.add(event)
        db.session.flush()

        # 2. Create Users (Super Admin and Field Coordinators)
        admin = User(
            username="admin",
            email="admin@sbitm.edu.in",
            role="admin",
            full_name="Prof. M. K. Agrawal (Cultural Patron)",
            phone="+91 9826012345",
            is_active=True
        )
        admin.set_password("sanskriti@2026")

        coord1 = User(
            username="coordinator1",
            email="coordinator1@sbitm.edu.in",
            role="coordinator",
            full_name="Aarav Sharma (General Secretary)",
            phone="+91 9826054321",
            is_active=True
        )
        coord1.set_password("blessings@2026")

        coord2 = User(
            username="coordinator2",
            email="coordinator2@sbitm.edu.in",
            role="coordinator",
            full_name="Ananya Deshmukh (Cultural Lead)",
            phone="+91 9826098765",
            is_active=True
        )
        coord2.set_password("blessings@2026")

        db.session.add_all([admin, coord1, coord2])
        db.session.flush()

        # 3. Create Sample Departments with Quotes & Lucide Icons
        depts_data = [
            {
                "name": "Computer Science & Engineering",
                "code": "CSE",
                "speciality": "Where Logic Meets Innovation.",
                "quote": "Code is poetry written in logic, and innovation is its greatest expression.",
                "hod_name": "Dr. Rajesh K. Varma",
                "icon_name": "cpu",
                "theme_color": "#C6A15B",
                "faculties": [
                    {"salutation": "Dr.", "name": "Rajesh K. Varma", "designation": "Professor & Head of Department", "cabin": "CS-101"},
                    {"salutation": "Prof.", "name": "Sunita Verma", "designation": "Associate Professor", "cabin": "CS-104"},
                    {"salutation": "Dr.", "name": "Amitabh Sen", "designation": "Assistant Professor", "cabin": "CS-108"},
                    {"salutation": "Prof.", "name": "Kavita Tiwari", "designation": "Assistant Professor", "cabin": "CS-112"}
                ]
            },
            {
                "name": "Artificial Intelligence & Data Science",
                "code": "AI & DS",
                "speciality": "Intelligence Beyond Imagination.",
                "quote": "The future belongs to those who transform data into possibilities.",
                "hod_name": "Dr. Sneha Pillai",
                "icon_name": "brain",
                "theme_color": "#D97732",
                "faculties": [
                    {"salutation": "Dr.", "name": "Sneha Pillai", "designation": "Head of Department & Professor", "cabin": "AI-201"},
                    {"salutation": "Prof.", "name": "Vikramaditya Roy", "designation": "Associate Professor", "cabin": "AI-205"},
                    {"salutation": "Dr.", "name": "Meera Nambiar", "designation": "Assistant Professor", "cabin": "AI-209"}
                ]
            },
            {
                "name": "Electronics & Communication Engineering",
                "code": "ECE",
                "speciality": "Connecting Ideas, Empowering Innovation.",
                "quote": "Every connection creates a new possibility.",
                "hod_name": "Dr. Harish Chandra Joshi",
                "icon_name": "radio",
                "theme_color": "#DFBA73",
                "faculties": [
                    {"salutation": "Dr.", "name": "Harish Chandra Joshi", "designation": "Professor & HOD", "cabin": "EC-301"},
                    {"salutation": "Prof.", "name": "Pooja Kulkarni", "designation": "Associate Professor", "cabin": "EC-305"},
                    {"salutation": "Prof.", "name": "Devendra Rathore", "designation": "Assistant Professor", "cabin": "EC-310"}
                ]
            },
            {
                "name": "Mechanical Engineering",
                "code": "ME",
                "speciality": "Engineering Motion, Building Tomorrow.",
                "quote": "Great things happen when imagination meets engineering.",
                "hod_name": "Dr. Balwant Singh Rajput",
                "icon_name": "settings",
                "theme_color": "#8A2635",
                "faculties": [
                    {"salutation": "Dr.", "name": "Balwant Singh Rajput", "designation": "Professor & HOD", "cabin": "ME-002"},
                    {"salutation": "Prof.", "name": "Alok Kumar Saxena", "designation": "Associate Professor", "cabin": "ME-008"},
                    {"salutation": "Prof.", "name": "Gaurav Upadhyay", "designation": "Assistant Professor", "cabin": "ME-014"}
                ]
            },
            {
                "name": "Civil Engineering",
                "code": "CE",
                "speciality": "Building Foundations, Creating Legacies.",
                "quote": "Every great structure begins with a strong foundation.",
                "hod_name": "Dr. Pradeep Bhattacharya",
                "icon_name": "building",
                "theme_color": "#C6A15B",
                "faculties": [
                    {"salutation": "Dr.", "name": "Pradeep Bhattacharya", "designation": "Professor & HOD", "cabin": "CE-102"},
                    {"salutation": "Prof.", "name": "Shalini Mishra", "designation": "Assistant Professor", "cabin": "CE-106"}
                ]
            },
            {
                "name": "Electrical Engineering",
                "code": "EE",
                "speciality": "Powering Progress, Illuminating Tomorrow.",
                "quote": "Energy drives the world, innovation drives its future.",
                "hod_name": "Dr. Arvind Narayan",
                "icon_name": "zap",
                "theme_color": "#E5C173",
                "faculties": [
                    {"salutation": "Dr.", "name": "Arvind Narayan", "designation": "Professor & HOD", "cabin": "EE-204"},
                    {"salutation": "Prof.", "name": "Ritu Srivastava", "designation": "Assistant Professor", "cabin": "EE-208"}
                ]
            },
            {
                "name": "Department of Management Studies",
                "code": "MBA",
                "speciality": "Leadership Begins With Vision.",
                "quote": "Great leaders don't just create opportunities; they create possibilities.",
                "hod_name": "Dr. Sandeep Chawla",
                "icon_name": "briefcase",
                "theme_color": "#D97732",
                "faculties": [
                    {"salutation": "Dr.", "name": "Sandeep Chawla", "designation": "Director & Professor of Management", "cabin": "MBA-401"},
                    {"salutation": "Prof.", "name": "Tanvi Gupta", "designation": "Associate Professor", "cabin": "MBA-405"}
                ]
            }
        ]

        created_faculties = []
        for d_info in depts_data:
            dept = Department(
                name=d_info["name"],
                code=d_info["code"],
                speciality=d_info["speciality"],
                quote=d_info["quote"],
                hod_name=d_info["hod_name"],
                icon_name=d_info["icon_name"],
                theme_color=d_info["theme_color"]
            )
            # Assign coordinators to departments
            dept.assigned_coordinators.append(coord1)
            dept.assigned_coordinators.append(coord2)
            db.session.add(dept)
            db.session.flush()

            for f_info in d_info["faculties"]:
                fac = Faculty(
                    department_id=dept.id,
                    salutation=f_info["salutation"],
                    name=f_info["name"],
                    designation=f_info["designation"],
                    cabin_number=f_info["cabin"],
                    email=f"{f_info['name'].lower().replace(' ', '.')}@sbitm.edu.in",
                    phone="+91 98260" + str(10000 + fac_count_global() if 'fac_count_global' in globals() else 12345),
                    is_active=True
                )
                db.session.add(fac)
                db.session.flush()
                created_faculties.append(fac)

        # 4. Seed Initial 3 Completed Approvals with Realistic Blessings
        sig_folder = app.config['SIGNATURE_FOLDER']
        selfie_folder = app.config['SELFIE_FOLDER']

        sample_blessings = [
            (created_faculties[0], "Dear Freshers, welcome to your transformational college journey! Learn with curiosity, innovate with passion, and make your institution proud."),
            (created_faculties[4], "Every dataset has a story; every new student has boundless potential. Never fear failure—it is the first iteration of breakthrough discovery."),
            (created_faculties[7], "Warmest blessings for Sanskriti 2026. Remember that the connections you forge today will become the foundation of your lifelong success.")
        ]

        for idx, (fac, blessing_txt) in enumerate(sample_blessings):
            sig_file, sig_b64 = create_sample_signature_image(sig_folder, fac.full_display_name)
            selfie_file, selfie_b64 = create_sample_selfie_image(selfie_folder, fac.full_display_name)

            approval = Approval(
                approval_uuid=str(uuid.uuid4()),
                event_id=event.id,
                department_id=fac.department_id,
                faculty_id=fac.id,
                coordinator_id=coord1.id if idx % 2 == 0 else coord2.id,
                status='approved',
                approval_time=datetime.now(timezone.utc) - timedelta(hours=(idx * 2 + 1)),
                ip_address="127.0.0.1",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
            )
            db.session.add(approval)
            db.session.flush()

            sig = FacultySignature(approval_id=approval.id, signature_filename=sig_file, signature_base64=sig_b64)
            slf = FacultySelfie(approval_id=approval.id, selfie_filename=selfie_file, selfie_base64=selfie_b64, capture_method='live_camera')
            msg = FacultyMessage(approval_id=approval.id, message_text=blessing_txt, is_public=True)
            con = ConsentRecord(
                approval_id=approval.id,
                invitation_accepted=True,
                signature_consented=True,
                selfie_consented=True,
                public_display_consented=True,
                consent_statement="Consented in person on coordinator mobile device"
            )
            hist = ApprovalHistory(
                approval_id=approval.id,
                action='submitted',
                performed_by_id=approval.coordinator_id,
                reason='On-site physical collection'
            )
            db.session.add_all([sig, slf, msg, con, hist])

        # Initial audit log
        init_audit = AuditLog(
            user_id=admin.id,
            action='system_initialized',
            target_model='Event',
            target_id=event.id,
            details='Sanskriti 2026 Digital Experience seeded with initial departments and faculty roster',
            ip_address="127.0.0.1"
        )
        db.session.add(init_audit)

        db.session.commit()
        print("Sanskriti 2026 database seeded successfully!")

