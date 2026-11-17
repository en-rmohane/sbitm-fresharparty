# SANSKRITI 2026 – Digital Freshers Invitation & Faculty Blessings Experience

[![Python](https://img.shields.io/badge/Python-3.10%2B-darkred.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-gold.svg)](https://flask.palletsprojects.com/)
[![Aesthetic](https://img.shields.io/badge/Theme-Royal%20Indian%20Festive-maroon.svg)](#brand-identity)
[![License](https://img.shields.io/badge/License-Proprietary%20College-orange.svg)](#)

---

## 🏛️ Project Vision

**SANSKRITI 2026** is a production-grade, full-stack digital invitation and faculty approval management system crafted for collegiate engineering institutions. 

It replaces the traditional paper invitation card that student organizers carried across campus with an enchanting, mobile-first festive experience. Campus coordinators physically visit department faculty members with a smartphone to present the grand digital invitation and collect:
1. **Interactive Invitation Viewing** with cinematic envelope opening and live countdown.
2. **Faculty E-Signature** drawn via finger, mouse, or stylus on an HTML5 canvas.
3. **Live Faculty Selfie** captured directly through the mobile front-facing camera.
4. **Faculty Words of Blessing** and guidance for the incoming freshman batch.
5. **Instant Digital Approval** stamped with date, time, coordinator metadata, and verification QR codes.

> **Privacy by Design:** Faculty members do not need to create accounts or remember passwords. Only authorized event coordinators and administrators log into the system. Faculty interact directly and comfortably on the coordinator's smartphone.

---

## 🎨 Brand Identity & Design System

The application combines the timeless elegance of an Indian royal wedding invitation, the exhilaration of a college cultural festival, and the precision of modern enterprise software.

| Color Name | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Primary Maroon** | `#641E28` | Primary branding, buttons, and headers |
| **Deep Maroon** | `#3A1019` | Royal backdrop and card foundations |
| **Antique Gold** | `#C6A15B` | Ornaments, borders, seals, and accents |
| **Saffron** | `#D97732` | Auspicious mantras and highlighted notes |
| **Ivory** | `#FFF8EB` | Invitation letter background and card surfaces |
| **Cream** | `#F5EBD9` | Secondary card fills and table alternating rows |
| **Dark Text** | `#29201E` | High-contrast readable typography |

### Typography
- **Headings & Titles:** Cinzel, Playfair Display
- **Body Text:** Poppins
- **Sacred Devotional Invocations:** Noto Sans Devanagari

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms, Werkzeug
- **Database:** SQLite (default for instant zero-config launch) with direct MySQL compatibility for enterprise deployment
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript ES6+, GSAP 3 (Cinematic envelope animation), Canvas API (Digital signatures), MediaDevices API (`getUserMedia` front camera), SweetAlert2, Lucide Icons, Chart.js (Real-time analytics), Canvas Confetti
- **Document & PDF Generation:** ReportLab, Pillow (PIL), QRCode
- **Architecture:** Modular Flask Blueprints (`departments`, `auth`, `coordinator`, `approvals`, `admin`, `reports`)

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10 or higher installed on your system.

### 2. Navigate to Project Directory
```powershell
cd C:\Users\ravik\.gemini\antigravity\scratch\sanskriti_2026
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python run.py
```
Open your web browser and navigate to:
**`http://127.0.0.1:5000`**

*(The database and initial academic departments are automatically initialized and pre-seeded on first run!)*

---

## 🔑 Default Credentials

For quick evaluation and testing, the following authorized accounts are pre-configured:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `sanskriti@2026` | Full event management, department CRUD, faculty roster, audit trail, approval reset |
| **Coordinator 1** | `coordinator1` | `blessings@2026` | General Secretary field account for on-site approval visits |
| **Coordinator 2** | `coordinator2` | `blessings@2026` | Cultural Lead field account for on-site approval visits |

---

## 📱 Mobile-First Faculty Approval Flow

When a coordinator visits a professor:
1. **Login & Select Department:** Coordinator opens portal on smartphone and taps into their assigned department.
2. **Select Faculty Dignitary:** Selects the faculty member from the live faculty roster.
3. **Welcome & Royal Invitation:** Shows a personalized welcome screen with the complete digital invitation card. Faculty reviews and acknowledges.
4. **Digital E-Signature:** Faculty signs smoothly with their finger or stylus on the responsive HTML5 canvas. Non-blank signatures are strictly validated.
5. **Live Selfie Capture:** Front-facing camera preview activates (`facingMode: "user"`). Coordinator captures faculty selfie with live preview, retake option, and safe fallback. Camera streams are immediately closed upon capture.
6. **Blessing Words & Public Consent:** Faculty can optionally share advice or blessings and choose whether to display their photo and message on the public Faculty Blessings Wall.
7. **Confirmation & Animated Stamp:** On confirmation, a golden **APPROVED** impact stamp animates with confetti, sacred temple chimes, and confirmation timestamps.

---

## 📑 Automated PDF Reports & QR Verification

The application includes built-in ReportLab generators for official college dossiers:
1. **Complete Event Approval Report:** Full campus roster of verified approvals with timestamps and coordinator badges.
2. **Faculty Blessings Anthology:** Commemorative publication compiling all words of wisdom bestowed by professors.
3. **Faculty Blessing Certificate:** Individual single-page certificate with digital signature, verification hash, and dynamic QR Code.
4. **Printable Royal Invitation Card:** Elegant printable card layout.
5. **Executive Summary Dossier:** Executive briefing of department completion tallies and percentages.
6. **Faculty Directory CSV:** Instant tabular export for administrative planning.

---

## 🛡️ Security & Privacy Compliance

- **Role-Based Access Control:** Separate routes for coordinators and administrators.
- **CSRF Protection:** Flask-WTF protects all mutations and AJAX submissions.
- **Biometric & Signature Vault:** Signatures and selfies are stored with randomized UUID filenames in protected server directories. Unauthorized public browsing of private selfies is strictly forbidden by server-side gatekeepers.
- **Immutable Audit Trail:** All approval submissions, resets, and configuration modifications are permanently logged with timestamps, actors, and IP addresses.
- **Statutory Notice:** Digital approval stamps are clearly disclaimed as internal collegiate ceremonial acknowledgments rather than legal identity certificates.

---

## 📂 Project Architecture

```
sanskriti_2026/
├── app/
│   ├── __init__.py           # Application factory & error handlers
│   ├── config.py             # Configuration re-export
│   ├── extensions.py         # SQLAlchemy, LoginManager, CSRF
│   ├── models.py             # Relational database models (12 models)
│   ├── seed.py               # Pre-seeded festive sample data
│   │
│   ├── admin/                # Blueprint: Super Admin console
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── approvals/            # Blueprint: Mobile wizard, verify, dashboard
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── auth/                 # Blueprint: Login, logout, session
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── coordinator/          # Blueprint: Field coordinator dashboard
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── departments/          # Blueprint: Landing page & Department universe
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── reports/              # Blueprint: ReportLab PDF generation & CSV
│   │   ├── __init__.py
│   │   ├── pdf_generator.py
│   │   └── routes.py
│   │
│   ├── static/
│   │   ├── css/              # style.css, animations.css, responsive.css
│   │   ├── js/               # main.js, animations.js, signature.js, camera.js, approval.js, dashboard.js
│   │   └── images/           # SVGs: logo, wax seal, diya, mandala, corner borders, approved stamp
│   │
│   └── templates/            # Jinja2 responsive templates (18 templates)
│       ├── base.html
│       ├── landing.html
│       ├── invitation.html
│       ├── department_universe.html
│       ├── admin/
│       ├── approvals/
│       ├── auth/
│       ├── coordinator/
│       └── reports/
│
├── instance/                 # SQLite database storage
├── uploads/                  # Protected biometric and signature vault
│   ├── signatures/
│   └── selfies/
├── config.py                 # Core application configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Main application runner
├── test_app.py               # Automated test suite
└── README.md                 # Documentation
```

---

*Designed and developed with Royal Indian Festive Aesthetics for SBITM Sanskriti 2026.*

