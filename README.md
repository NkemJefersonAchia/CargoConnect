# 🚛 CargoConnect

> A full-stack logistics and relocation web platform built for **Kigali, Rwanda**.
> CargoConnect connects customers who need to move cargo or relocate with verified truck drivers — in real time.

---

## 📌 Table of Contents

- [What is CargoConnect?](#what-is-cargoconnect)
- [How it Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Team Members](#team-members)
- [Task Sheet](#task-sheet)
- [Requirements](#requirements)
- [Setup on macOS](#setup-on-macos)
- [Setup on Windows](#setup-on-windows)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Creating an Admin Account](#creating-an-admin-account)
- [API Overview](#api-overview)
- [Common Issues](#common-issues)

---

## What is CargoConnect?

CargoConnect is a web application that makes it easy to book a truck for moving cargo, furniture, or household goods around Kigali. Think of it like Uber — but for trucks and cargo.

**Three types of users:**

| Role | What they do |
|------|-------------|
| **Customer** | Search for trucks, book a driver, track the truck live on a map, pay via MTN MoMo |
| **Driver** | Go online/offline, accept or decline job requests, share live GPS location, complete trips |
| **Admin** | Verify drivers, manage all users and bookings, view platform-wide statistics |

---

## How it Works

1. A **customer** registers and opens the dashboard
2. They fill in pickup address, dropoff address, cargo weight, and preferred time
3. The app finds **available, verified drivers** nearby using the Haversine distance formula
4. The customer picks a driver and confirms the booking
5. The **driver** gets a notification, reviews the job, and accepts it
6. The customer can **track the truck live** on a Leaflet map as the driver shares GPS updates
7. When the trip is done, the driver marks it complete
8. Payment is sent via **MTN MoMo** and both parties are notified
9. The customer leaves a **star rating** for the driver

---

## Features

### Customer
- Register and log in securely (passwords are bcrypt hashed — never stored as plain text)
- Dashboard with live stats: total bookings, completed trips, pending bookings, total spent in RWF
- Book a truck — search by cargo weight, pickup/dropoff address, and preferred date/time
- Smart driver matching sorted by rating, with estimated cost shown upfront
  - Cost formula: 2,000 RWF base fare + 500 RWF per ton + 200 RWF per km
- Live GPS tracking of the driver on an interactive map — no page refresh needed
- View full booking history with colour-coded status badges
- Receive in-app notifications (booking confirmed, trip completed, payment updates)
- Rate the driver 1–5 stars after a completed trip with an optional written comment

### Driver
- Register with a licence number (account waits for admin verification before going live)
- Go online/offline with a large toggle switch on the dashboard
- See incoming job requests with customer details and estimated earnings
- Accept or decline individual jobs with one click
- Share live GPS location to the customer using the browser's geolocation API
- Mark trip as completed to trigger the payment flow
- View job history with past earnings and ratings received

### Admin
- Full control dashboard with 6 platform-wide statistics cards
- Driver verification queue — approve or reject new driver applications
- Manage all users — search in real time by name/email/role, delete accounts
- Manage all drivers — toggle availability, remove verification, delete records
- View and filter all bookings by status (pending / confirmed / completed / cancelled)
- Full booking detail modal showing payment and trip information

### Payment (MTN MoMo)
- Payment initiated via the MTN Mobile Money sandbox Collections API
- Customer receives a payment prompt directly on their phone
- Webhook callback automatically updates the payment record in the database
- Both customer and driver are notified on payment success or failure
- If the MoMo API is unreachable, the payment stays pending and a retry notification is sent

### Real-Time GPS Tracking
- Driver location updates travel over WebSocket using Socket.IO
- Customer's map marker moves live without any page refresh
- Each booking has its own private Socket.IO room for security
- Works from any modern browser that supports the Geolocation API

---

## Tech Stack

| Layer | Technology | Why we chose it |
|-------|-----------|-----------------|
| Backend language | Python 3 | Readable, fast to build with, huge ecosystem |
| Web framework | Flask | Lightweight and unopinionated — we control the structure |
| Real-time | Flask-SocketIO + eventlet | WebSocket support for live GPS without polling |
| Database | PostgreSQL 16+ | Reliable, production-grade relational database |
| ORM | SQLAlchemy + Flask-SQLAlchemy | Clean Python objects instead of raw SQL |
| Schema migrations | Flask-Migrate (Alembic) | Safe, versioned database schema changes |
| Auth | Flask-Login + Flask-Bcrypt | Session management + industry-standard password hashing |
| Frontend | Vanilla HTML5, CSS3, JavaScript | No framework overhead — every line does exactly what you read |
| Maps | Leaflet.js + OpenStreetMap | Free, open-source, works great for Kigali |
| Payments | MTN MoMo Collections API | The dominant mobile money platform in Rwanda |
| Fonts | Google Fonts (Syne + DM Sans) | Clean, modern typography that loads fast |
| Version control | Git + GitHub | Collaboration and full code history |

---

## Project Structure

```
CargoConnect/
│
├── app.py                  # Entry point — creates the Flask app and starts the server
├── extensions.py           # Shared Flask extensions (db, bcrypt, socketio, migrate, login)
├── requirements.txt        # All Python packages the app needs
├── .env                    # Your secret config — never commit this file
├── .env.example            # Safe template showing what variables are needed
│
├── config/
│   └── config.py           # Reads .env and applies settings to the Flask app
│
├── models/                 # Database tables defined as Python classes (SQLAlchemy ORM)
│   ├── __init__.py         # Imports db from extensions
│   ├── user.py             # users table — one row per account, shared across all roles
│   ├── customer.py         # customers table — extra profile info for customer accounts
│   ├── driver.py           # drivers table — licence, rating, GPS coordinates, availability
│   ├── truck.py            # trucks table — truck plate and capacity, linked to a driver
│   ├── booking.py          # bookings table — a trip from pickup to dropoff
│   ├── payment.py          # payments table — one payment record per booking
│   ├── rating.py           # ratings table — star rating submitted after a trip
│   └── notification.py     # notifications table — in-app messages for any user
│
├── routes/                 # URL handlers grouped into Flask Blueprints
│   ├── __init__.py
│   ├── auth.py             # /auth  — login, register, logout
│   ├── booking.py          # /booking — search for drivers, create/cancel bookings
│   ├── driver.py           # /driver — availability toggle, accept/decline/complete jobs
│   ├── customer.py         # /customer — dashboard stats, bookings, notifications, ratings
│   ├── tracking.py         # (root) — Socket.IO GPS events for live tracking
│   ├── payment.py          # /payment — MTN MoMo initiation and callback
│   └── admin.py            # /admin — all admin management endpoints
│
├── templates/              # HTML pages rendered by Flask using Jinja2 templating
│   ├── base.html                 # Shared page layout with sidebar and topbar
│   ├── login.html                # Login form
│   ├── register.html             # Registration form with customer/driver role toggle
│   ├── customer_dashboard.html   # Customer home — stats, active trip, booking form
│   ├── book_truck.html           # Dedicated truck search page
│   ├── track_booking.html        # Live Leaflet map for tracking a trip
│   ├── driver_dashboard.html     # Driver home — availability toggle, job queue
│   ├── driver_job.html           # Active job detail with GPS share button
│   ├── admin_dashboard.html      # Admin overview with verification queue
│   ├── admin_users.html          # User management table with live search
│   ├── admin_drivers.html        # Driver management table
│   └── admin_bookings.html       # Bookings table with status filter
│
└── static/
    ├── css/
    │   └── style.css       # All styles — every colour and size is a CSS variable
    └── js/
        ├── auth.js         # Handles the role toggle on the register form
        ├── booking.js      # Truck search form, results display, booking modal
        ├── tracking.js     # Leaflet map setup and Socket.IO live location listener
        ├── dashboard.js    # Sidebar hamburger for mobile and shared helper functions
        └── admin.js        # Admin table utilities and confirmation modals
```

---

## Team Members

| Name | Role |
|------|------|
| *(Add name)* | *(e.g. Backend Developer)* |
| *(Add name)* | *(e.g. Frontend Developer)* |
| *(Add name)* | *(e.g. Database & DevOps)* |
| *(Add name)* | *(e.g. UI/UX Designer)* |

---

## Task Sheet

📋 **Team Task Sheet:** *(Paste your Google Sheets / Notion / Trello link here)*

---

## Requirements

Make sure the following are installed on your computer **before** you start.

| Tool | Minimum Version | Download Link |
|------|----------------|---------------|
| Python | 3.10 | [python.org/downloads](https://www.python.org/downloads/) |
| PostgreSQL | 14 | [postgresql.org/download](https://www.postgresql.org/download/) |
| Git | Any recent | [git-scm.com](https://git-scm.com) |

> **Never used these before?**
> - **Python** is the programming language the backend is written in.
> - **PostgreSQL** is the database — it stores all users, bookings, payments, etc.
> - **Git** downloads the project code from GitHub to your computer.

---

## Setup on macOS

Follow every step in order. Do not skip any step.

### Step 1 — Download the project code

Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter) and run:

```bash
git clone https://github.com/your-username/CargoConnect.git
cd CargoConnect
```

### Step 2 — Install PostgreSQL

The easiest option on Mac is the free app **Postgres.app**:

1. Go to [postgresapp.com](https://postgresapp.com) and download the latest version
2. Drag **Postgres.app** to your **Applications** folder and open it
3. Click **Initialize**, then click **Start**
4. In the app window, click the button labeled **"Configure your $PATH"** — this lets Terminal use the `psql` command

### Step 3 — Create the database

In Terminal, run:

```bash
createdb cargoconnect
```

If nothing is printed and no error appears, the database was created successfully.

### Step 4 — Create a virtual environment

A virtual environment keeps this project's packages isolated from the rest of your computer. Think of it as a private box for this project.

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt should now start with `(venv)` — that means it is active.

### Step 5 — Install all Python packages

```bash
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, Socket.IO, bcrypt, and everything else the app needs. It may take 1–2 minutes.

### Step 6 — Create your environment file

```bash
cp .env.example .env
```

Open `.env` in VS Code, TextEdit, or nano, and update these two lines:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://YOUR_MAC_USERNAME@localhost:5432/cargoconnect
```

To find your Mac username, run this in Terminal:
```bash
whoami
```

For example, if `whoami` prints `john`, your DATABASE_URL should be:
```
DATABASE_URL=postgresql://john@localhost:5432/cargoconnect
```

> Note: no password is needed — Postgres.app uses your Mac account to authenticate automatically.

### Step 7 — Start the app

```bash
python app.py
```

When you see this line, the app is ready:
```
wsgi starting up on http://0.0.0.0:5000
```

Open your browser and visit: **http://localhost:5000** 🎉

To stop the app later: press `Ctrl + C` in the Terminal window.

---

## Setup on Windows

Follow every step in order. Use **Command Prompt** or **PowerShell** (search for either in the Start menu).

### Step 1 — Download the project code

```cmd
git clone https://github.com/your-username/CargoConnect.git
cd CargoConnect
```

### Step 2 — Install PostgreSQL

1. Go to [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) and click **Download the installer**
2. Run the installer — leave all settings as default
3. When asked to set a password for the `postgres` user, write something simple like `postgres` — **write it down, you will need it later**
4. Keep port **5432** (the default)
5. Complete the installation and click Finish

### Step 3 — Create the database

Open **SQL Shell (psql)** from the Windows Start menu (it was installed with PostgreSQL).

- Press **Enter** four times to accept the defaults for Server, Database, Port, and Username
- When asked for **Password**, type the password you set during installation

Then type this command and press Enter:

```sql
CREATE DATABASE cargoconnect;
```

Then type `\q` and press Enter to exit.

### Step 4 — Create a virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

Your prompt should now start with `(venv)`.

### Step 5 — Install all Python packages

```cmd
pip install -r requirements.txt
```

### Step 6 — Create your environment file

```cmd
copy .env.example .env
```

Open `.env` in Notepad or VS Code and update these two lines:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/cargoconnect
```

Replace `YOUR_PASSWORD` with the PostgreSQL password you created during installation.

### Step 7 — Start the app

```cmd
python app.py
```

When you see this line, the app is ready:
```
wsgi starting up on http://0.0.0.0:5000
```

Open your browser and visit: **http://localhost:5000** 🎉

To stop the app later: press `Ctrl + C`.

---

## Environment Variables

All secrets and settings go in a file called `.env` in the project root. This file is in `.gitignore` so it is **never uploaded to GitHub**.

| Variable | What it is | Example |
|----------|-----------|---------|
| `SECRET_KEY` | A random string Flask uses to protect sessions and cookies. Make up anything. | `my-secret-key-abc123` |
| `DATABASE_URL` | How to connect to PostgreSQL | `postgresql://john@localhost:5432/cargoconnect` |
| `MOMO_API_KEY` | Your API key from the MTN MoMo developer portal | *(from sandbox.momodeveloper.mtn.com)* |
| `MOMO_USER_ID` | Your user ID from the MTN MoMo developer portal | *(from sandbox.momodeveloper.mtn.com)* |
| `MOMO_BASE_URL` | The MoMo API server address | `https://sandbox.momodeveloper.mtn.com` |
| `MOMO_SUBSCRIPTION_KEY` | MoMo subscription key | *(from sandbox.momodeveloper.mtn.com)* |
| `FLASK_ENV` | Set to `development` while building. Change to `production` before deploying. | `development` |
| `FLASK_DEBUG` | `1` shows detailed error pages in the browser. Set to `0` before going live. | `1` |

---

## Running the App

Every time you want to work on the project, do this:

```bash
# macOS — activate the virtual environment
source venv/bin/activate

# Windows — activate the virtual environment
venv\Scripts\activate

# Start the server
python app.py
```

Then open **http://localhost:5000** in your browser.

Make sure **Postgres.app is open and running** (macOS) before starting, or the database will not connect.

---

## Creating an Admin Account

The public registration page only allows `customer` and `driver` roles. To promote an account to admin:

**Step 1:** Register a normal account at http://localhost:5000/auth/register

**Step 2:** Open your terminal and connect to the database:

macOS:
```bash
psql -U YOUR_MAC_USERNAME cargoconnect
```

Windows:
```cmd
psql -U postgres cargoconnect
```

**Step 3:** Run this SQL command, replacing the email with your registered email:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
\q
```

**Step 4:** Log out and log back in — you will now see the **Admin Dashboard**.

---

## API Overview

Every API endpoint returns JSON in this exact shape:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Human readable description"
}
```

On error:
```json
{
  "status": "error",
  "data": null,
  "message": "Description of what went wrong"
}
```

### Authentication (`/auth`)
| Method | URL | What it does |
|--------|-----|-------------|
| GET/POST | `/auth/login` | Show login page / submit login |
| GET/POST | `/auth/register` | Show registration page / create account |
| GET | `/auth/logout` | Log out and redirect to login |

### Bookings (`/booking`)
| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/booking/search` | Find available drivers near pickup location |
| POST | `/booking/create` | Create a new booking |
| GET | `/booking/<id>` | Get details of one booking |
| POST | `/booking/<id>/cancel` | Cancel a pending booking |

### Customer (`/customer`)
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/customer/dashboard` | Render the customer dashboard page |
| GET | `/customer/stats` | Numbers for the 4 stat cards |
| GET | `/customer/active-booking` | The current confirmed booking (if any) |
| GET | `/customer/recent-bookings` | Last 5 bookings |
| GET | `/customer/notifications` | Unread notifications count and list |
| POST | `/customer/notifications/mark-read` | Mark all notifications as read |
| POST | `/customer/rate/<id>` | Submit a star rating for a completed trip |

### Driver (`/driver`)
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/driver/dashboard` | Render the driver dashboard page |
| GET | `/driver/stats` | Numbers for the 4 stat cards |
| PATCH | `/driver/availability` | Toggle online / offline status |
| GET | `/driver/pending-jobs` | All pending job requests for this driver |
| GET | `/driver/active-job` | The current confirmed job (if any) |
| POST | `/driver/job/<id>/accept` | Accept a pending booking |
| POST | `/driver/job/<id>/decline` | Decline a pending booking |
| POST | `/driver/job/<id>/complete` | Mark a confirmed trip as completed |
| GET | `/driver/job-history` | Last 10 completed jobs |

### Payments (`/payment`)
| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/payment/initiate/<id>` | Initiate MTN MoMo payment for a booking |
| POST | `/payment/callback` | MoMo webhook — updates payment status |

### Admin (`/admin`)
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/admin/dashboard` | Render admin overview page |
| GET | `/admin/stats` | 6 platform-wide statistics |
| GET | `/admin/unverified-drivers` | Drivers waiting for verification |
| POST | `/admin/drivers/<id>/verify` | Verify a driver |
| DELETE | `/admin/drivers/<id>/reject` | Reject and remove an unverified driver |
| GET | `/admin/users` | All users |
| DELETE | `/admin/users/<id>` | Delete a user account |
| GET | `/admin/drivers` | All drivers |
| PATCH | `/admin/drivers/<id>/toggle-availability` | Toggle a driver's availability |
| PATCH | `/admin/drivers/<id>/remove-verification` | Remove a driver's verified status |
| DELETE | `/admin/drivers/<id>` | Delete a driver record |
| GET | `/admin/bookings` | All bookings (add `?status=pending` to filter) |

### Real-Time Socket.IO Events
| Event name | Who sends it | What it does |
|-----------|-------------|-------------|
| `join_tracking_room` | Customer browser | Joins the live tracking room for their booking |
| `driver_location_update` | Driver browser | Sends GPS coordinates to the server |
| `location_update` | Server | Broadcasts new driver coordinates to the customer's map |

---

## Common Issues

**`role "username" does not exist`**
Your `.env` file still has the placeholder text. Open `.env` and replace `username` in `DATABASE_URL` with your actual system username (run `whoami` to find it).

**`Connection refused` on port 5432**
PostgreSQL is not running. On macOS, open Postgres.app. On Windows, open Services in Task Manager and start the PostgreSQL service.

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment is not active. Run `source venv/bin/activate` (macOS) or `venv\Scripts\activate` (Windows) and try again.

**`Address already in use` — port 5000**
Something else is already using port 5000. Stop that process, or change the port in `app.py`:
```python
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```
Then visit http://localhost:5001.

**Page loads but shows a database error after submitting a form**
Make sure the `cargoconnect` database was created (Step 3 in setup) and that `DATABASE_URL` in `.env` points to it correctly.

**Eventlet deprecation warning in the terminal**
This is a warning, not an error — the app runs fine. You can safely ignore it during development.

---

## License

This project was built as an academic project for Trimester 4.
