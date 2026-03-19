#!/usr/bin/env python3
"""Generate CargoConnect_Teamwork_Report.pdf using reportlab"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak,
                                 KeepTogether)
from reportlab.platypus import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ---- Colors ----
NAVY   = colors.HexColor('#0A1F44')
ORANGE = colors.HexColor('#E85D04')
BG     = colors.HexColor('#F4F6FB')
WHITE  = colors.white
TEXT   = colors.HexColor('#334155')
MUTED  = colors.HexColor('#6B7280')
BORDER = colors.HexColor('#DDE3EF')
GREEN  = colors.HexColor('#065F46')
GREEN_BG = colors.HexColor('#D1FAE5')
ORANGE_LIGHT = colors.HexColor('#FFF7ED')
ORANGE_BORDER = colors.HexColor('#F9BD8A')

PW, PH = A4
ML, MR, MT, MB = 2*cm, 2*cm, 2.2*cm, 2.2*cm

# ---- Styles ----
base = getSampleStyleSheet()

def S(name, parent='Normal', **kw):
    return ParagraphStyle(name, parent=base[parent], **kw)

styles = {
    'h1':   S('h1',   fontSize=28, fontName='Helvetica-Bold',
               textColor=NAVY, spaceAfter=6, leading=32),
    'h2':   S('h2',   fontSize=18, fontName='Helvetica-Bold',
               textColor=NAVY, spaceBefore=18, spaceAfter=8, leading=22),
    'h3':   S('h3',   fontSize=11, fontName='Helvetica-Bold',
               textColor=ORANGE, spaceBefore=12, spaceAfter=6,
               leading=14, textTransform='uppercase', letterSpacing=0.5),
    'body': S('body', fontSize=11, fontName='Helvetica',
               textColor=TEXT, spaceAfter=6, leading=17),
    'bullet': S('bullet', fontSize=11, fontName='Helvetica',
                textColor=TEXT, spaceAfter=4, leading=16,
                leftIndent=14, firstLineIndent=-14),
    'code':  S('code', fontSize=9, fontName='Courier',
                textColor=colors.HexColor('#E2E8F0'),
                backColor=colors.HexColor('#1E2A3A'),
                spaceAfter=6, leading=14, leftIndent=10),
    'tag':   S('tag', fontSize=8, fontName='Helvetica-Bold',
               textColor=ORANGE, spaceAfter=2, textTransform='uppercase',
               letterSpacing=1.5),
    'muted': S('muted', fontSize=9, fontName='Helvetica',
               textColor=MUTED, spaceAfter=4),
    'cover_title': S('cover_title', fontSize=36, fontName='Helvetica-Bold',
                     textColor=NAVY, leading=42, spaceAfter=6),
    'cover_sub':   S('cover_sub', fontSize=16, fontName='Helvetica',
                     textColor=MUTED, spaceAfter=20),
    'th':    S('th', fontSize=9, fontName='Helvetica-Bold',
               textColor=WHITE, leading=12),
    'td':    S('td', fontSize=10, fontName='Helvetica',
               textColor=TEXT, leading=14),
    'meeting_title': S('meeting_title', fontSize=12, fontName='Helvetica-Bold',
                       textColor=NAVY, spaceAfter=3),
    'meeting_date':  S('meeting_date', fontSize=10, fontName='Helvetica-Bold',
                       textColor=ORANGE, spaceAfter=4),
    'link':  S('link', fontSize=10, fontName='Helvetica',
               textColor=colors.HexColor('#1D4ED8'), spaceAfter=4),
}

def P(text, style='body'):
    return Paragraph(text, styles[style])

def B(text, bold_prefix=None):
    if bold_prefix:
        return Paragraph(
            f'<bullet>\u2022</bullet> <b>{bold_prefix}:</b> {text}',
            styles['bullet'])
    return Paragraph(f'<bullet>\u2022</bullet> {text}', styles['bullet'])

def ph(label, desc, height=3*cm):
    """Screenshot placeholder as a table."""
    inner = [
        [Paragraph(f'[ SCREENSHOT PLACEHOLDER ]', styles['tag'])],
        [Paragraph(label, ParagraphStyle('ph_label', fontSize=11,
                   fontName='Helvetica-Bold', textColor=NAVY, leading=14))],
        [Paragraph(desc, ParagraphStyle('ph_desc', fontSize=9,
                   fontName='Helvetica', textColor=MUTED, leading=12))],
    ]
    t = Table(inner, colWidths=[PW - ML - MR - 4])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG),
        ('BOX',        (0,0), (-1,-1), 1, BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING',   (0,0), (-1,-1), 16),
        ('RIGHTPADDING',  (0,0), (-1,-1), 16),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def orange_card(title, body_text):
    inner = [
        [Paragraph(title, styles['h3'])],
        [Paragraph(body_text, styles['body'])],
    ]
    t = Table(inner, colWidths=[PW - ML - MR - 4])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ORANGE_LIGHT),
        ('BOX',        (0,0), (-1,-1), 1, ORANGE_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
    ]))
    return t

def section_header_flowable(title, num):
    """Section header as a table with navy background."""
    t = Table([[Paragraph(f'<font color="#E85D04"><b>{num}</b></font>  '
                          f'<font color="white"><b>{title}</b></font>',
                          ParagraphStyle('sh', fontSize=14, fontName='Helvetica-Bold',
                                         textColor=WHITE, leading=18))]],
              colWidths=[PW - ML - MR])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
    ]))
    return t

def meeting_block(title, date, points, ph_label, ph_desc):
    rows = [
        [Paragraph(title, styles['meeting_title']),
         Paragraph(date, styles['meeting_date'])],
    ]
    for pt in points:
        rows.append([Paragraph(f'\u2022  {pt}', styles['bullet']), ''])
    rows.append([ph(ph_label, ph_desc, height=1.8*cm), ''])
    t = Table(rows, colWidths=[(PW - ML - MR)*0.68, (PW - ML - MR)*0.32])
    t.setStyle(TableStyle([
        ('BOX',        (0,0), (-1,-1), 1, BORDER),
        ('BACKGROUND', (0,0), (-1,0), BG),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('SPAN', (0, len(rows)-1), (1, len(rows)-1)),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [WHITE, BG]),
    ]))
    return t

def std_table(header_row, data_rows, col_widths=None):
    cw = col_widths or [(PW - ML - MR) / len(header_row)] * len(header_row)
    header = [Paragraph(h, styles['th']) for h in header_row]
    rows = [header]
    for dr in data_rows:
        rows.append([Paragraph(str(c), styles['td']) for c in dr])
    t = Table(rows, colWidths=cw, repeatRows=1)
    bg_rows = [(0, i, -1, i) for i in range(2, len(rows), 2)]
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.5, BORDER),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]
    for (r0, r1, r2, r3) in bg_rows:
        style_cmds.append(('BACKGROUND', (r0, r1), (r2, r3), BG))
    t.setStyle(TableStyle(style_cmds))
    return t

# ======== PAGE TEMPLATES ========
def on_page(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, PH - 1.2*cm, PW, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, PH - 1.25*cm, PW, 0.12*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(ML, PH - 0.85*cm, 'CargoConnect')
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(PW - MR, PH - 0.85*cm, 'Teamwork and Project Management Report')
    # Footer
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PW, 1.0*cm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(ML, 0.38*cm, 'March 2026  |  Trimester 4')
    canvas.drawRightString(PW - MR, 0.38*cm, f'Page {doc.page}')
    canvas.restoreState()

def on_cover(canvas, doc):
    canvas.saveState()
    # Orange top bar
    canvas.setFillColor(ORANGE)
    canvas.rect(0, PH - 0.6*cm, PW, 0.6*cm, fill=1, stroke=0)
    # Navy bottom bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PW, 1.4*cm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(ML, 0.55*cm, 'CargoConnect  |  Teamwork and Project Management Report  |  March 2026')
    canvas.restoreState()

# ======== BUILD STORY ========
story = []

# ---- COVER PAGE ----
story.append(Spacer(1, 3*cm))
story.append(Paragraph('<font color="#E85D04">___</font>', styles['h1']))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph('<b>CargoConnect</b>', styles['cover_title']))
story.append(Paragraph('Teamwork and Project Management Report', styles['cover_sub']))
story.append(Spacer(1, 1.5*cm))
cover_meta = [
    ['Course', 'Full-Stack Web Development, Trimester 4'],
    ['Project Name', 'CargoConnect - Smart Logistics Platform for Kigali'],
    ['Team Name', '[ INSERT TEAM NAME ]'],
    ['Team Members', '[Member 1]   |   [Member 2]   |   [Member 3]   |   [Member 4]'],
    ['Submission Date', 'March 2026'],
    ['Document Type', 'Teamwork Report (PDF Submission)'],
]
cw = cover_meta
ct = Table([[Paragraph(f'<b>{r[0]}</b>', styles['td']),
             Paragraph(r[1], styles['td'])] for r in cover_meta],
           colWidths=[5*cm, PW - ML - MR - 5*cm])
ct.setStyle(TableStyle([
    ('BOX',        (0,0), (-1,-1), 1, BORDER),
    ('GRID',       (0,0), (-1,-1), 0.5, BORDER),
    ('BACKGROUND', (0,0), (0,-1), BG),
    ('TOPPADDING',    (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(ct)
story.append(Spacer(1, 1.5*cm))
story.append(P('This report documents the project management tools, team collaboration '
               'practices, communication methods, and current implementation state of the '
               'CargoConnect platform. It accompanies the technical presentation slides '
               'submitted for the Trimester 4 technical progress review.', 'muted'))
story.append(PageBreak())

# ---- PAGE 2: PROJECT MANAGEMENT TOOLS ----
story.append(section_header_flowable("Project Management Tools", "1"))
story.append(Spacer(1, 0.4*cm))
story.append(P('The CargoConnect team used the following tools for task tracking, sprint '
               'planning, and progress monitoring throughout the development cycle.'))

tools_data = [
    ['GitHub Projects', 'Task board and sprint planning',
     'Kanban board: Backlog, In Progress, Review, Done. Each feature linked to a GitHub issue.'],
    ['GitHub Issues', 'Bug tracking and feature requests',
     'Issues labeled by type (feature, bug, enhancement) and assigned to team members.'],
    ['GitHub (Version Control)', 'Source code collaboration',
     'Feature branches per member; pull requests required for merging into main.'],
    ['[ Trello / Notion ]', 'Meeting notes and documentation',
     'Meeting agendas, decisions, and action items recorded after each team session.'],
    ['WhatsApp / Discord', 'Daily communication',
     'Quick questions, status updates, and code sharing between formal meetings.'],
]
story.append(std_table(['Tool', 'Purpose', 'How It Was Used'],
                       tools_data, [4*cm, 4*cm, 8.5*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(P('The GitHub Projects board was the primary task-tracking tool. '
               'Tasks were organized across the following columns and updated after '
               'every development session:', 'body'))
for col, desc in [
    ('Backlog', 'All planned features and known bugs not yet assigned'),
    ('In Progress', 'Tasks actively being worked on; one task per member at a time'),
    ('Review', 'Completed tasks awaiting peer review before merging'),
    ('Done', 'Merged and tested features'),
]:
    story.append(B(desc, col))
story.append(Spacer(1, 0.3*cm))
story.append(ph('Screenshot: GitHub Projects Kanban Board',
                'Insert screenshot of the GitHub Projects board showing tasks distributed '
                'across Backlog, In Progress, Review, and Done columns with team member assignments.'))
story.append(Spacer(1, 0.5*cm))

story.append(P('<b>Task Distribution - Main Development Sprint</b>', 'h3'))
task_data = [
    ['User authentication (login, register, bcrypt)', '[Member 1]', 'Done', '#[ ]'],
    ['Role-based access control decorators', '[Member 1]', 'Done', '#[ ]'],
    ['Booking search and Haversine algorithm', '[Member 2]', 'Done', '#[ ]'],
    ['Booking lifecycle (create, confirm, cancel)', '[Member 2]', 'Done', '#[ ]'],
    ['SocketIO real-time GPS tracking', '[Member 3]', 'Done', '#[ ]'],
    ['Leaflet.js map integration', '[Member 3]', 'Done', '#[ ]'],
    ['MTN MoMo API integration and callback', '[Member 4]', 'Done', '#[ ]'],
    ['Admin dashboard and driver verification', '[Member 4]', 'Done', '#[ ]'],
    ['Database schema design (all 8 models)', 'All members', 'Done', '#[ ]'],
    ['Frontend templates (all 14 pages)', 'All members', 'Done', '#[ ]'],
]
story.append(std_table(['Task', 'Assigned To', 'Status', 'GitHub Issue'],
                       task_data, [9*cm, 2.5*cm, 1.8*cm, 1.8*cm]))
story.append(PageBreak())

# ---- PAGE 3: TEAM COLLABORATION ----
story.append(section_header_flowable("Team Collaboration", "2"))
story.append(Spacer(1, 0.4*cm))
story.append(P('2.1  Team Meetings Log', 'h2'))
story.append(P('The team held regular meetings throughout the trimester. '
               'The following log summarizes the key meetings, dates, and discussion points.'))

meetings = [
    ("Meeting 1: Project Kickoff and Scope Definition", "[ INSERT DATE ]",
     ["Defined the problem statement: lack of organized cargo transport in Kigali",
      "Agreed on the tech stack: Flask, PostgreSQL, SocketIO, MTN MoMo",
      "Identified three user roles: customer, driver, admin",
      "Assigned initial responsibilities per team member"],
     "Screenshot: Meeting 1", "Insert screenshot (video call, whiteboard photo, or notes)"),
    ("Meeting 2: Database Schema Review", "[ INSERT DATE ]",
     ["Reviewed all 8 SQLAlchemy models and their relationships",
      "Agreed on using PostgreSQL ENUM types for status fields",
      "Resolved FK chain: users -> customers/drivers -> trucks -> bookings",
      "Confirmed one-to-one payment per booking (UNIQUE constraint)"],
     "Screenshot: Meeting 2", "Insert screenshot of whiteboard ERD or shared document"),
    ("Meeting 3: API Design and Blueprint Structure", "[ INSERT DATE ]",
     ["Finalized blueprint structure: auth, booking, driver, customer, tracking, payment, admin",
      "Agreed on standard JSON response envelope for all endpoints",
      "Reviewed Haversine algorithm and cost formula implementation",
      "Discussed SocketIO room-per-booking pattern for live tracking"],
     "Screenshot: Meeting 3", "Insert screenshot of shared screen or API design notes"),
    ("Meeting 4: MTN MoMo Integration Review", "[ INSERT DATE ]",
     ["Walked through MoMo sandbox setup and API key configuration",
      "Designed the async callback flow for payment status updates",
      "Agreed on notification strategy for payment success and failure",
      "Tested initiation endpoint against sandbox; verified 202 response"],
     "Screenshot: Meeting 4", "Insert screenshot of test results or code review session"),
    ("Meeting 5: Pre-Presentation Review and QA", "[ INSERT DATE ]",
     ["End-to-end walkthrough of all user flows (customer, driver, admin)",
      "Identified and resolved role enforcement gaps in early admin routes",
      "Standardized response envelopes across all blueprints",
      "Divided presentation sections per team member for rehearsal"],
     "Screenshot: Meeting 5", "Insert screenshot of presentation rehearsal or QA run"),
]

for mtitle, mdate, mpoints, mph_label, mph_desc in meetings:
    story.append(KeepTogether([
        Table([[Paragraph(f'<b>{mtitle}</b>', styles['meeting_title']),
                Paragraph(mdate, styles['meeting_date'])],
               *[[Paragraph(f'\u2022  {pt}', styles['bullet']), '']
                 for pt in mpoints]],
              colWidths=[(PW-ML-MR)*0.72, (PW-ML-MR)*0.28],
              style=TableStyle([
                  ('BOX',        (0,0), (-1,-1), 1, BORDER),
                  ('BACKGROUND', (0,0), (-1,0), BG),
                  ('TOPPADDING',    (0,0), (-1,-1), 6),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                  ('LEFTPADDING',   (0,0), (-1,-1), 10),
              ])),
        Spacer(1, 0.2*cm),
        ph(mph_label, mph_desc, 1.8*cm),
        Spacer(1, 0.4*cm),
    ]))

story.append(PageBreak())

# ---- PAGE 4: COMMUNICATION ----
story.append(section_header_flowable("Team Collaboration (continued)", "2"))
story.append(Spacer(1, 0.4*cm))
story.append(P('2.2  Communication and Collaboration Practices', 'h2'))

for item in [
    ('Version control', 'GitHub with feature branches named by feature (e.g. feature/booking-api). '
     'Pull requests required one reviewer approval before merging into main.'),
    ('Daily standups', 'Brief written updates posted to WhatsApp/Discord: what was done, '
     'what is in progress, and any blockers. Kept the whole team in sync without full meetings.'),
    ('Code review', 'Pull request reviews included inline comments on logic, naming, and docstrings. '
     'All feedback resolved before merge.'),
    ('Design sharing', 'Figma frames shared with all team members. Everyone reviewed UI '
     'before implementation to reduce misalignment between design and code.'),
    ('Task handoff', 'When a backend endpoint was completed, the developer posted the URL '
     'and request/response format to the group channel for immediate frontend integration.'),
]:
    story.append(B(item[1], item[0]))

story.append(Spacer(1, 0.5*cm))
story.append(P('2.3  GitHub Contribution Evidence', 'h2'))
story.append(ph('Screenshot: GitHub Commit History',
                'Insert screenshot of the GitHub repository commit history showing commits from all '
                'team members, including branch names, commit messages, and timestamps.'))
story.append(Spacer(1, 0.4*cm))
story.append(ph('Screenshot: GitHub Pull Requests',
                'Insert screenshot of closed pull requests showing feature branches merged into main, '
                'reviewer assignments, and approval records.'))
story.append(Spacer(1, 0.4*cm))
story.append(orange_card(
    'REPOSITORY LINK',
    '<b>GitHub URL:</b> [ INSERT GITHUB REPOSITORY LINK HERE ]<br/>'
    '<b>Branch Strategy:</b> main (production-ready) + feature branches per task<br/>'
    '<b>Total Commits:</b> [ INSERT NUMBER ]<br/>'
    '<b>Contributors:</b> 4 team members'
))
story.append(Spacer(1, 0.5*cm))
story.append(P('2.4  Individual Contribution Breakdown', 'h2'))
contrib_data = [
    ('[Member 1]', 'Authentication and Backend Architecture',
     'Flask app factory, user auth (login/register/logout), role decorators, app config, blueprint registration'),
    ('[Member 2]', 'Booking System and Algorithm',
     'Haversine algorithm, driver search with subquery filtering, cost estimation, booking CRUD, status state machine'),
    ('[Member 3]', 'Real-Time Tracking and Frontend',
     'Flask-SocketIO integration, per-booking rooms, GPS persistence, Leaflet.js map, JS SocketIO client, tracking UI'),
    ('[Member 4]', 'Payments and Admin',
     'MTN MoMo API integration, async callback, in-app notifications, admin dashboard stats, driver verification queue'),
]
story.append(std_table(['Member', 'Technical Area', 'Key Contributions'],
                       contrib_data, [2.8*cm, 4.0*cm, 9.3*cm]))
story.append(PageBreak())

# ---- PAGE 5: PROGRESS DOCUMENTATION ----
story.append(section_header_flowable("Progress Documentation", "3"))
story.append(Spacer(1, 0.4*cm))
story.append(P('3.1  Figma Design', 'h2'))
story.append(P('The team produced UI designs in Figma before frontend implementation. '
               'All screens follow the CargoConnect design system: Navy #0A1F44, Orange #E85D04, '
               'Syne typeface for headings, and DM Sans for body text.'))
story.append(orange_card('FIGMA ACCESS LINK',
                         '<b>URL:</b> [ INSERT FIGMA LINK HERE ]<br/>'
                         'Evaluators can access the design with view-only permissions.'))
story.append(Spacer(1, 0.3*cm))
story.append(ph('Screenshot: Figma Design Frames',
                'Insert screenshot showing all screens in Figma: login, customer dashboard, '
                'booking flow, live tracking map, driver dashboard, and admin panel.'))
story.append(Spacer(1, 0.5*cm))

story.append(P('3.2  Database Design and Schema', 'h2'))
story.append(ph('Screenshot: Database ERD',
                'Insert screenshot of the entity-relationship diagram (ERD) exported from pgAdmin, '
                'DBeaver, or dbdiagram.io, showing all 8 tables and their foreign key relationships: '
                'users, customers, drivers, trucks, bookings, payments, ratings, notifications.'))
story.append(Spacer(1, 0.5*cm))

story.append(P('3.3  Frontend Implementation', 'h2'))
for label, desc in [
    ('Screenshot: Customer Dashboard',
     'customer_dashboard.html showing booking history and active booking tracker'),
    ('Screenshot: Driver Dashboard',
     'driver_dashboard.html showing job queue, availability toggle, and weekly earnings'),
    ('Screenshot: Live Tracking Map',
     'track_booking.html showing Leaflet.js map with live driver marker and booking info'),
    ('Screenshot: Admin Dashboard',
     'admin_dashboard.html showing platform statistics: total users, bookings, and revenue'),
]:
    story.append(ph(label, desc))
    story.append(Spacer(1, 0.25*cm))
story.append(PageBreak())

# ---- PAGE 6: BACKEND / API ----
story.append(section_header_flowable("Progress Documentation (continued)", "3"))
story.append(Spacer(1, 0.4*cm))
story.append(P('3.4  Backend and API Implementation', 'h2'))
story.append(P('The backend is a Flask application with 7 blueprints and 44 registered routes. '
               'The following screenshots document the running application and API behavior.'))
for label, desc in [
    ('Screenshot: Flask App Running (Terminal)',
     'Insert screenshot of the terminal showing the Flask server starting at 0.0.0.0:5000 '
     'with all blueprints registered and SocketIO initialized.'),
    ('Screenshot: API Response (Postman or Browser DevTools)',
     'Insert screenshot of a successful API call (e.g. POST /booking/search or GET /admin/stats) '
     'showing the standard {status, data, message} JSON envelope.'),
    ('Screenshot: PostgreSQL Database (pgAdmin or psql)',
     'Insert screenshot showing the cargoconnect database with all 8 tables visible '
     '(users, customers, drivers, trucks, bookings, payments, ratings, notifications).'),
]:
    story.append(ph(label, desc))
    story.append(Spacer(1, 0.3*cm))

story.append(P('3.5  Summary of Implemented Endpoints', 'h2'))
endpoint_data = [
    ['auth', '/auth', 'GET/POST /login, GET/POST /register, GET /logout'],
    ['booking', '/booking', 'POST /search, POST /create, GET /<id>, POST /<id>/cancel'],
    ['driver', '/driver', 'GET /dashboard, GET /stats, PATCH /availability, GET /pending-jobs, '
                          'GET /active-job, POST /job/<id>/accept, POST /job/<id>/decline, '
                          'POST /job/<id>/complete, GET /job-history'],
    ['customer', '/customer', 'GET /dashboard, GET /bookings, GET /notifications'],
    ['tracking', '/', 'GET /track/<id>;  SocketIO: join_tracking_room, driver_location_update, location_update'],
    ['payment', '/payment', 'POST /initiate/<id>,  POST /callback'],
    ['admin', '/admin', 'GET /dashboard, GET /stats, GET|DELETE /users, GET|DELETE /drivers, '
                        'POST /drivers/<id>/verify, GET /bookings, PATCH /toggle-availability'],
]
story.append(std_table(['Blueprint', 'URL Prefix', 'Key Endpoints'],
                       endpoint_data, [2.5*cm, 2.8*cm, 10.8*cm]))
story.append(PageBreak())

# ---- PAGE 7: CLOSING ----
story.append(section_header_flowable("Summary and Declarations", "4"))
story.append(Spacer(1, 0.4*cm))
story.append(P('The CargoConnect team has successfully completed all core features of the platform '
               'within the Trimester 4 development cycle. The application delivers a fully functional, '
               'role-separated logistics platform with real-time GPS tracking, automated cost estimation, '
               'MTN MoMo payment integration, and an admin oversight panel.'))
story.append(Spacer(1, 0.2*cm))
story.append(P('The team maintained consistent collaboration through regular meetings, GitHub-based '
               'version control with pull request reviews, and clear task ownership per member. '
               'All feedback from previous reviews has been incorporated into the current implementation.'))

story.append(Spacer(1, 0.5*cm))
story.append(P('4.1  Project Links', 'h2'))
story.append(std_table(['Resource', 'Link'],
                       [['GitHub Repository', '[ INSERT GITHUB LINK ]'],
                        ['Figma Design', '[ INSERT FIGMA LINK ]'],
                        ['Live Demo (if deployed)', '[ INSERT LINK or N/A ]']],
                       [5*cm, 11.1*cm]))

story.append(Spacer(1, 0.5*cm))
story.append(P('4.2  Declarations', 'h2'))
story.append(P('All code in the CargoConnect repository represents original work by the named '
               'team members. External libraries and APIs are listed in the References slide of '
               'the presentation and cited appropriately. All team members have reviewed this '
               'report and confirm its accuracy.'))
story.append(Spacer(1, 0.8*cm))
story.append(std_table(['Member Name', 'Role', 'Signature'],
                       [['[Member 1]', '[ INSERT ROLE ]', '________________'],
                        ['[Member 2]', '[ INSERT ROLE ]', '________________'],
                        ['[Member 3]', '[ INSERT ROLE ]', '________________'],
                        ['[Member 4]', '[ INSERT ROLE ]', '________________']],
                       [6*cm, 5*cm, 5.1*cm]))

# ======== BUILD ========
out = '/Users/nkemachia/Documents/Trimester_4/CargoConnect/CargoConnect_Teamwork_Report.pdf'
doc = SimpleDocTemplate(
    out,
    pagesize=A4,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT + 1.2*cm, bottomMargin=MB + 1.0*cm,
    title='CargoConnect Teamwork Report',
    author='CargoConnect Team',
)
doc.build(story,
          onFirstPage=on_cover,
          onLaterPages=on_page)
print(f"Saved: {out}")
