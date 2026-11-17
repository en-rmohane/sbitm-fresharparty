import os
import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Sanskriti Brand Colors
MAROON = colors.HexColor('#641E28')
DEEP_MAROON = colors.HexColor('#3A1019')
ANTIQUE_GOLD = colors.HexColor('#C6A15B')
GOLD_LIGHT = colors.HexColor('#FFEBB8')
SAFFRON = colors.HexColor('#D97732')
IVORY = colors.HexColor('#FFF8EB')
CREAM = colors.HexColor('#F5EBD9')
DARK_TEXT = colors.HexColor('#29201E')

def get_sanskriti_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='SanskritiTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=MAROON,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='SanskritiSubtitle',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=ANTIQUE_GOLD,
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='SanskritiHeading',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=DEEP_MAROON,
        spaceBefore=10,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='SanskritiBody',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=DARK_TEXT
    ))

    styles.add(ParagraphStyle(
        name='SanskritiQuote',
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=DEEP_MAROON,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='SanskritiCenter',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=DARK_TEXT,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='SanskritiSmall',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.gray,
        alignment=TA_CENTER
    ))

    return styles


def generate_invitation_pdf(event):
    """Generates a royal printable invitation card PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = get_sanskriti_styles()
    story = []

    # Auspicious Header
    story.append(Paragraph("॥ श्री गणेशाय नमः ॥", styles['SanskritiSubtitle']))
    story.append(Spacer(1, 10))

    # College Name
    story.append(Paragraph(event.college_name.upper(), styles['SanskritiSubtitle']))
    story.append(Paragraph("Cordially Requests the Honour of Your Presence At", styles['SanskritiCenter']))
    story.append(Spacer(1, 15))

    # Event Title
    story.append(Paragraph(event.title, styles['SanskritiTitle']))
    story.append(Paragraph(f'"{event.tagline}"', styles['SanskritiQuote']))
    story.append(Spacer(1, 15))

    # Invitation Narrative
    story.append(Paragraph(event.invitation_text, styles['SanskritiCenter']))
    story.append(Spacer(1, 20))

    # Event Logistics Box
    data = [
        [
            Paragraph("<b>EVENT DATE:</b>", styles['SanskritiBody']),
            Paragraph(event.event_date, styles['SanskritiBody'])
        ],
        [
            Paragraph("<b>EVENT TIME:</b>", styles['SanskritiBody']),
            Paragraph(event.event_time, styles['SanskritiBody'])
        ],
        [
            Paragraph("<b>VENUE:</b>", styles['SanskritiBody']),
            Paragraph(event.venue, styles['SanskritiBody'])
        ],
        [
            Paragraph("<b>ORGANIZED BY:</b>", styles['SanskritiBody']),
            Paragraph(event.organizer_details, styles['SanskritiBody'])
        ]
    ]
    t = Table(data, colWidths=[1.8 * inch, 4.2 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('BOX', (0, 0), (-1, -1), 1.5, ANTIQUE_GOLD),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, ANTIQUE_GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 25))

    story.append(Paragraph("Let's make this beginning memorable with your divine presence!", styles['SanskritiQuote']))
    story.append(Spacer(1, 15))

    # Footer note
    story.append(HRFlowable(width="80%", thickness=1, color=ANTIQUE_GOLD, spaceAfter=10))
    story.append(Paragraph(f"Official Invitation Dossier • {event.title} • {event.college_short_name}", styles['SanskritiSmall']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_event_approval_report_pdf(event, approvals):
    """Generates the Complete Event Approval Report PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = get_sanskriti_styles()
    story = []

    # Title
    story.append(Paragraph(event.college_name.upper(), styles['SanskritiSubtitle']))
    story.append(Paragraph(f"{event.title} – FACULTY APPROVALS DOSSIER", styles['SanskritiTitle']))
    story.append(Paragraph(f"Generated On: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['SanskritiSmall']))
    story.append(Spacer(1, 15))

    # Summary Stats
    story.append(Paragraph("<b>Campus Approval Summary</b>", styles['SanskritiHeading']))
    total_approved = len(approvals)
    summary_data = [
        ["Total Faculty Blessings Recorded", str(total_approved)],
        ["Event Date", event.event_date],
        ["Audit Status", "Verified & Sanctified"]
    ]
    st = Table(summary_data, colWidths=[3.2 * inch, 3.2 * inch])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('BOX', (0, 0), (-1, -1), 1, ANTIQUE_GOLD),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(st)
    story.append(Spacer(1, 18))

    # Roster Table
    story.append(Paragraph("<b>Verified Faculty Approvals Roster</b>", styles['SanskritiHeading']))
    headers = ["#", "Faculty Dignitary", "Department", "Date & Time", "Coordinator", "Public"]
    table_data = [headers]

    for idx, app in enumerate(approvals, start=1):
        is_pub = "Yes" if (app.consent and app.consent.public_display_consented) else "Private"
        table_data.append([
            str(idx),
            app.faculty.full_display_name,
            app.department.code,
            app.approval_time.strftime('%d-%b %I:%M %p'),
            app.coordinator.full_name,
            is_pub
        ])

    rt = Table(table_data, colWidths=[0.4 * inch, 2.2 * inch, 0.9 * inch, 1.4 * inch, 1.2 * inch, 0.7 * inch])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), MAROON),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CREAM]),
    ]))
    story.append(rt)

    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph("This document contains verified college archival records for Sanskriti 2026.", styles['SanskritiSmall']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_faculty_blessings_pdf(event, approvals):
    """Generates the Faculty Blessings Anthology publication."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = get_sanskriti_styles()
    story = []

    story.append(Paragraph("॥ वाक् शुभाशीषम् ॥", styles['SanskritiSubtitle']))
    story.append(Paragraph(f"{event.title} – FACULTY BLESSINGS ANTHOLOGY", styles['SanskritiTitle']))
    story.append(Paragraph("Words of Wisdom, Guidance & Encouragement from Our Respected Faculty", styles['SanskritiQuote']))
    story.append(Spacer(1, 15))

    for app in approvals:
        msg = app.message.message_text if (app.message and app.message.message_text) else "Warmest welcome and blessings to the incoming freshmen of Sanskriti 2026!"
        
        card_content = [
            [Paragraph(f"<b>{app.faculty.full_display_name}</b> — <i>{app.faculty.designation}, Department of {app.department.name}</i>", styles['SanskritiHeading'])],
            [Paragraph(f'“{msg}”', styles['SanskritiQuote'])],
            [Paragraph(f"<font size=8 color=gray>Auspicious acknowledgment recorded on {app.approval_time.strftime('%B %d, %Y')} • Verified by {app.coordinator.full_name}</font>", styles['SanskritiBody'])]
        ]
        
        t = Table(card_content, colWidths=[6.4 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CREAM),
            ('BOX', (0, 0), (-1, -1), 1, ANTIQUE_GOLD),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_faculty_card_pdf(approval, verification_url):
    """Generates a commemorative single-page Certificate & Blessing Receipt for a faculty member."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = get_sanskriti_styles()
    story = []

    event = approval.event
    story.append(Paragraph("॥ कृतज्ञता पत्रम् ॥", styles['SanskritiSubtitle']))
    story.append(Paragraph("CERTIFICATE OF FACULTY BLESSING", styles['SanskritiTitle']))
    story.append(Paragraph(f"{event.college_name}", styles['SanskritiSubtitle']))
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        f"This is to gratefully acknowledge that <b>{approval.faculty.full_display_name}</b>, "
        f"{approval.faculty.designation} in the <b>Department of {approval.department.name}</b>, "
        f"has cordially acknowledged the digital invitation for <b>{event.title}</b> "
        f"and bestowed their auspicious blessings upon the incoming students.",
        styles['SanskritiBody']
    ))
    story.append(Spacer(1, 15))

    # Words of Blessing if any
    msg = approval.message.message_text if (approval.message and approval.message.message_text) else "Warmest welcome and heartiest congratulations to the Freshers!"
    story.append(Paragraph(f'“{msg}”', styles['SanskritiQuote']))
    story.append(Spacer(1, 15))

    # Generate QR Code image in-memory for verification
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    rl_qr = RLImage(qr_buffer, width=1.3 * inch, height=1.3 * inch)

    # Details table with QR
    details_data = [
        [
            Paragraph(f"<b>Verification ID:</b><br/>{approval.approval_uuid}<br/><br/>"
                      f"<b>Timestamp:</b> {approval.approval_time.strftime('%B %d, %Y at %I:%M %p')}<br/>"
                      f"<b>Field Coordinator:</b> {approval.coordinator.full_name}<br/>"
                      f"<b>Status:</b> Digitally Sanctified &amp; Archived", styles['SanskritiBody']),
            rl_qr
        ]
    ]
    t = Table(details_data, colWidths=[4.8 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('BOX', (0, 0), (-1, -1), 1.2, ANTIQUE_GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Internal college acknowledgment. Not a statutory legal identity certificate.", styles['SanskritiSmall']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_final_summary_pdf(event, departments, total_faculty, approved_count):
    """Generates the Executive Final Summary PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = get_sanskriti_styles()
    story = []

    story.append(Paragraph(event.college_name.upper(), styles['SanskritiSubtitle']))
    story.append(Paragraph(f"{event.title} – FINAL APPROVAL SUMMARY", styles['SanskritiTitle']))
    story.append(Paragraph(f"Campus Blessings Completion Dossier • {datetime.now().strftime('%B %d, %Y')}", styles['SanskritiQuote']))
    story.append(Spacer(1, 15))

    # Department breakdown table
    headers = ["Department Code", "Department Name", "Total Faculty", "Blessings Received", "Status"]
    table_data = [headers]

    for d in departments:
        app_cnt = d.approved_count(event.id)
        tot_cnt = d.total_faculty_count()
        status = "100% Completed" if (tot_cnt > 0 and app_cnt >= tot_cnt) else f"{app_cnt}/{tot_cnt}"
        table_data.append([
            d.code,
            d.name,
            str(tot_cnt),
            str(app_cnt),
            status
        ])

    t = Table(table_data, colWidths=[1.1 * inch, 2.5 * inch, 1.1 * inch, 1.3 * inch, 1.2 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), MAROON),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, ANTIQUE_GOLD),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CREAM]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Overall Campus Score:</b> {approved_count} of {total_faculty} Faculty Blessings Sanctified.", styles['SanskritiHeading']))
    story.append(Paragraph("With the blessings of our respected faculty, we are ready to welcome a new generation.", styles['SanskritiQuote']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

