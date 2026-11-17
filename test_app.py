import os
import sys
import unittest
import base64
from app import create_app
from app.extensions import db
from app.models import User, Event, Department, Faculty, Approval

class Sanskriti2026TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def test_01_database_seeded(self):
        with self.app.app_context():
            event = Event.query.first()
            self.assertIsNotNone(event)
            self.assertEqual(event.title, "SANSKRITI 2026")

            depts = Department.query.all()
            self.assertGreaterEqual(len(depts), 7)

            faculty_count = Faculty.query.count()
            self.assertGreaterEqual(faculty_count, 15)

            admin = User.query.filter_by(username="admin").first()
            self.assertIsNotNone(admin)
            self.assertTrue(admin.check_password("sanskriti@2026"))

            coord = User.query.filter_by(username="coordinator1").first()
            self.assertIsNotNone(coord)
            self.assertTrue(coord.check_password("blessings@2026"))

            approvals = Approval.query.all()
            self.assertGreaterEqual(len(approvals), 3)
            print("[OK] Database seeding verified successfully.")

    def test_02_public_pages(self):
        endpoints = [
            '/',
            '/invitation',
            '/departments',
            '/approvals/blessings-wall',
            '/approvals/journey',
            '/approvals/dashboard',
            '/approvals/grand-finale',
            '/approvals/api/stats',
            '/reports/',
            '/auth/login'
        ]
        for ep in endpoints:
            response = self.client.get(ep)
            self.assertEqual(response.status_code, 200, f"Endpoint {ep} failed with status {response.status_code}")
        print("[OK] All public endpoints return HTTP 200.")

    def test_03_pdf_generation(self):
        pdf_endpoints = [
            '/reports/download/invitation-pdf',
            '/reports/download/event-report-pdf',
            '/reports/download/blessings-pdf',
            '/reports/download/final-summary-pdf',
            '/reports/export/faculty-csv'
        ]
        for ep in pdf_endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200)
            self.assertGreater(len(res.data), 100)
        print("[OK] ReportLab PDF generation and CSV export return valid files.")

    def test_04_coordinator_workflow(self):
        # 1. Login as coordinator1
        login_res = self.client.post('/auth/login', data={
            'username': 'coordinator1',
            'password': 'blessings@2026'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome", login_res.data)

        # 2. Access coordinator dashboard
        dash_res = self.client.get('/coordinator/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Welcome Dignitary Coordinator", dash_res.data)

        # 3. Access Department Faculty List
        with self.app.app_context():
            dept = Department.query.first()
            dept_id = dept.id
        dept_res = self.client.get(f'/coordinator/department/{dept_id}')
        self.assertEqual(dept_res.status_code, 200)

        # 4. Find an unapproved faculty member
        with self.app.app_context():
            event = Event.query.first()
            unapproved_faculty = None
            for f in Faculty.query.all():
                if not f.has_approved(event.id):
                    unapproved_faculty = f
                    break
            self.assertIsNotNone(unapproved_faculty, "Need at least one unapproved faculty for test")
            fac_id = unapproved_faculty.id
            fac_name = unapproved_faculty.full_display_name

        # 5. Access Approval Wizard
        wiz_res = self.client.get(f'/coordinator/faculty/{fac_id}/approval')
        self.assertEqual(wiz_res.status_code, 200)
        self.assertIn(fac_name.encode('utf-8'), wiz_res.data)

        # 6. Submit Approval via API
        # Create minimal 1x1 base64 png
        tiny_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        submit_payload = {
            'faculty_id': fac_id,
            'event_id': event.id,
            'department_id': unapproved_faculty.department_id,
            'signature_base64': tiny_png,
            'selfie_base64': tiny_png,
            'capture_method': 'live_camera',
            'message_text': 'May wisdom and kindness guide every step of the Sanskriti 2026 freshers!',
            'is_public': True
        }
        submit_res = self.client.post('/approvals/api/submit', json=submit_payload)
        self.assertEqual(submit_res.status_code, 200)
        json_data = submit_res.get_json()
        self.assertTrue(json_data['success'])
        uuid_str = json_data['approval_uuid']

        # 7. Access Approval Success Celebration Screen
        succ_res = self.client.get(f'/approvals/success/{uuid_str}')
        self.assertEqual(succ_res.status_code, 200)
        self.assertIn(b"Thank You for Your Valuable Blessings", succ_res.data)

        # 8. Access QR Verification Link
        ver_res = self.client.get(f'/approvals/verify/{uuid_str}')
        self.assertEqual(ver_res.status_code, 200)
        self.assertIn(b"BLESSING VERIFICATION", ver_res.data)

        print("[OK] Coordinator workflow and digital approval submission passed.")

    def test_05_admin_controls(self):
        # 1. Login as admin
        self.client.get('/auth/logout')
        login_res = self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'sanskriti@2026'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # 2. Access Admin Console Pages
        admin_pages = [
            '/admin/dashboard',
            '/admin/event-settings',
            '/admin/departments',
            '/admin/faculty',
            '/admin/coordinators',
            '/admin/approvals',
            '/admin/audit-logs'
        ]
        for p in admin_pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Admin page {p} failed with {res.status_code}")

        print("[OK] Admin console and security authorizations passed.")

if __name__ == '__main__':
    unittest.main()
