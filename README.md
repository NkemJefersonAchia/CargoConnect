# CargoConnect

> A full-stack logistics and relocation web platform built for **Kigali, Rwanda**.
> CargoConnect connects customers who need to move cargo or relocate with verified truck drivers, in real time.

---

## Table of Contents

- [What is CargoConnect?](#what-is-cargoconnect)
- [How it Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup on macOS](#setup-on-macos)
- [Setup on Windows](#setup-on-windows)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Creating an Admin Account](#creating-an-admin-account)
- [All Routes](#all-routes)
- [API Overview](#api-overview)
- [Socket.IO Events](#socketio-events)
- [Common Issues](#common-issues)
- [Team Members](#team-members)

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
  - Cost formula: `2,000 RWF base fare + 500 RWF per ton + 200 RWF per km`
- Live GPS tracking of the driver on an interactive map — no page refresh needed
- View full booking history with colour-coded status badges
- Receive in-app notifications (booking confirmed, trip completed, payment updates) with mark-as-read
- Rate the driver 1–5 stars after a completed trip with an optional written comment
- Profile section showing account name, email, and phone

### Driver
- Register with a licence number (account waits for admin verification before going live)
- Go online/offline with a large toggle switch on the dashboard
- See incoming job requests with customer details and estimated earnings
- Accept or decline individual jobs with one click
- Share live GPS location to the customer using the browser's geolocation API
- Mark trip as completed to trigger the payment flow
- View job history with past earnings and ratings received
- My Truck section showing registered truck plate and capacity
- Profile section showing licence, rating, and verification status

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
│   ├── tracking.py         # (root) — live tracking page + Socket.IO GPS events
│   ├── payment.py          # /payment — MTN MoMo initiation and callback
│   └── admin.py            # /admin — all admin management endpoints
│
├── templates/              # HTML pages rendered by Flask using Jinja2 templating
│   ├── base.html                 # Shared layout — sidebar, topbar, flash messages
│   ├── login.html                # Login form
│   ├── register.html             # Registration form with customer/driver role toggle
│   ├── customer_dashboard.html   # Customer home — stats, bookings, notifications, profile
│   ├── book_truck.html           # Standalone truck search page
│   ├── track_booking.html        # Live Leaflet map for tracking a trip
│   ├── driver_dashboard.html     # Driver home — jobs, truck info, profile
│   ├── driver_job.html           # Active job detail with GPS share and complete buttons
│   ├── admin_dashboard.html      # Admin overview with verification queue
│   ├── admin_users.html          # User management table with live search
│   ├── admin_drivers.html        # Driver management table
│   └── admin_bookings.html       # Bookings table with status filter
│
└── static/
    ├── css/
    │   └── style.css       # All styles — every colour and size is a CSS variable
    └── js/
        ├── auth.js         # Role toggle on register form; auto-dismiss flash messages
        ├── booking.js      # Customer dashboard: stats, bookings, truck search, notifications
        ├── tracking.js     # Leaflet map setup and Socket.IO live location listener
        ├── dashboard.js    # Sidebar hamburger for mobile; shared formatRWF/formatDate helpers
        └── admin.js        # Admin table utilities and confirmation modals
```

---

## Requirements

Make sure the following are installed on your computer **before** you start.

| Tool | Minimum Version | Download Link |
|------|----------------|---------------|
| Python | 3.10 | [python.org/downloads](https://www.python.org/downloads/) |
| PostgreSQL | 14 | [postgresql.org/download](https://www.postgresql.org/download/) |
| Git | Any recent | [git-scm.com](https://git-scm.com) |

---

## Setup on macOS

Follow every step in order.

### Step 1 — Download the project code

Open **Terminal** and run:

```bash
git clone https://github.com/NkemJefersonAchia/CargoConnect.git
cd CargoConnect
```

### Step 2 — Install PostgreSQL

The easiest option on Mac is the free app **Postgres.app**:

1. Go to [postgresapp.com](https://postgresapp.com) and download the latest version
2. Drag **Postgres.app** to your **Applications** folder and open it
3. Click **Initialize**, then click **Start**
4. Click **"Configure your $PATH"** — this lets Terminal use the `psql` command

### Step 3 — Create the database

```bash
createdb cargoconnect
```

### Step 4 — Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt should now start with `(venv)`.

### Step 5 — Install all Python packages

```bash
pip install -r requirements.txt
```

### Step 6 — Create your environment file

```bash
cp .env.example .env
```

Open `.env` and update:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://YOUR_MAC_USERNAME@localhost:5432/cargoconnect
```

To find your Mac username:
```bash
whoami
```

For example, if `whoami` returns `john`:
```
DATABASE_URL=postgresql://john@localhost:5432/cargoconnect
```

### Step 7 — Start the app

```bash
python app.py
```

When you see this line, the app is ready:
```
wsgi starting up on http://0.0.0.0:5000
```

Open your browser and go to: **http://localhost:5000**

To stop the app: press `Ctrl + C`.

---

## Setup on Windows

### Step 1 — Download the project code

```cmd
git clone https://github.com/NkemJefersonAchia/CargoConnect.git
cd CargoConnect
```

### Step 2 — Install PostgreSQL

1. Go to [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) and click **Download the installer**
2. Run the installer — leave all settings as default
3. When asked, set a password for the `postgres` user — **write it down**
4. Keep port **5432**

### Step 3 — Create the database

Open **SQL Shell (psql)** from the Windows Start menu.

Press **Enter** four times, then type your password when prompted.

```sql
CREATE DATABASE cargoconnect;
\q
```

### Step 4 — Create a virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 5 — Install all Python packages

```cmd
pip install -r requirements.txt
```

### Step 6 — Create your environment file

```cmd
copy .env.example .env
```

Open `.env` and update:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/cargoconnect
```

### Step 7 — Start the app

```cmd
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## Environment Variables

All secrets and settings go in `.env` in the project root. This file is never committed to GitHub.

| Variable | What it is | Example |
|----------|-----------|---------|
| `SECRET_KEY` | Random string Flask uses to protect sessions | `my-secret-key-abc123` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://john@localhost:5432/cargoconnect` |
| `MOMO_API_KEY` | MTN MoMo sandbox API key | *(from sandbox.momodeveloper.mtn.com)* |
| `MOMO_USER_ID` | MTN MoMo sandbox user ID | *(from sandbox.momodeveloper.mtn.com)* |
| `MOMO_BASE_URL` | MoMo API server address | `https://sandbox.momodeveloper.mtn.com` |
| `MOMO_SUBSCRIPTION_KEY` | MoMo subscription key | *(from sandbox.momodeveloper.mtn.com)* |
| `FLASK_ENV` | `development` while building | `development` |
| `FLASK_DEBUG` | `1` shows detailed error pages in browser | `1` |

---

## Running the App

Every time you want to work on the project:

```bash
# macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Start the server
python app.py
```

Then open **http://localhost:5000**.

---

## Creating an Admin Account

The public registration page only allows `customer` and `driver` roles. To promote an account to admin:

**Step 1:** Register a normal account at `http://localhost:5000/auth/register`

**Step 2:** Connect to the database:

```bash
# macOS
psql -U YOUR_MAC_USERNAME cargoconnect

# Windows
psql -U postgres cargoconnect
```

**Step 3:** Run this SQL (replace the email):

```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
\q
```

**Step 4:** Log out and log back in — you will see the **Admin Dashboard**.

---

## All Routes

### Page Routes (render HTML)

| Method | URL | Template | Who can access |
|--------|-----|----------|----------------|
| GET/POST | `/auth/login` | `login.html` | Anyone |
| GET/POST | `/auth/register` | `register.html` | Anyone |
| GET | `/auth/logout` | — (redirect) | Logged-in users |
| GET | `/customer/dashboard` | `customer_dashboard.html` | Customers only |
| GET | `/driver/dashboard` | `driver_dashboard.html` | Drivers only |
| GET | `/driver/job/<id>` | `driver_job.html` | Drivers only |
| GET | `/track/<booking_id>` | `track_booking.html` | Logged-in users |
| GET | `/admin/dashboard` | `admin_dashboard.html` | Admins only |
| GET | `/admin/users-page` | `admin_users.html` | Admins only |
| GET | `/admin/drivers-page` | `admin_drivers.html` | Admins only |
| GET | `/admin/bookings-page` | `admin_bookings.html` | Admins only |

### Customer Sidebar Navigation

| Link | Destination | What it shows |
|------|------------|---------------|
| Dashboard | `/customer/dashboard` | Full dashboard page |
| My Bookings | `#recent` | Recent bookings table (on dashboard) |
| Book a Truck | `#quickbook` | Booking search form (on dashboard) |
| Notifications | `#notifications` | Unread notifications list (on dashboard) |
| My Profile | `#profile` | Account info section (on dashboard) |

### Driver Sidebar Navigation

| Link | Destination | What it shows |
|------|------------|---------------|
| Dashboard | `/driver/dashboard` | Full dashboard page |
| My Jobs | `#jobs` | Incoming job requests (on dashboard) |
| My Truck | `#truck` | Truck plate and capacity (on dashboard) |
| Earnings | `#history` | Job history table (on dashboard) |
| My Profile | `#profile` | Driver account info (on dashboard) |

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
| GET | `/customer/stats` | Numbers for the 4 stat cards |
| GET | `/customer/active-booking` | Current confirmed booking (if any) |
| GET | `/customer/recent-bookings` | Last 5 bookings |
| GET | `/customer/notifications` | Unread notifications count and list |
| POST | `/customer/notifications/mark-read` | Mark all notifications as read |
| POST | `/customer/rate/<id>` | Submit a star rating for a completed trip |

### Driver (`/driver`)
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/driver/stats` | Numbers for the 4 stat cards |
| PATCH | `/driver/availability` | Toggle online / offline status |
| GET | `/driver/pending-jobs` | All pending job requests for this driver |
| GET | `/driver/active-job` | Current confirmed job (if any) |
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

---

## Socket.IO Events

| Event name | Direction | What it does |
|-----------|-----------|-------------|
| `join_tracking_room` | Customer → Server | Customer joins the live tracking room for their booking |
| `driver_location_update` | Driver → Server | Driver sends GPS coordinates to the server |
| `location_update` | Server → Customer | Server broadcasts new driver coordinates to the customer's map |
| `joined` | Server → Customer | Confirmation that the customer joined the room |

---

## Common Issues

**`role "username" does not exist`**
Your `.env` file still has placeholder text. Open `.env` and replace `username` in `DATABASE_URL` with your actual system username (run `whoami` to find it).

**`Connection refused` on port 5432**
PostgreSQL is not running. On macOS, open Postgres.app. On Windows, open Services in Task Manager and start the PostgreSQL service.

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment is not active. Run `source venv/bin/activate` (macOS) or `venv\Scripts\activate` (Windows).

**`Address already in use` — port 5000**
Something else is already using port 5000. On macOS, AirPlay Receiver uses port 5000 — go to **System Settings → General → AirDrop & Handoff** and turn it off. Or change the port in `app.py`:
```python
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```
Then visit http://localhost:5001.

**Page loads but shows a database error after submitting a form**
Make sure the `cargoconnect` database was created and that `DATABASE_URL` in `.env` is correct.

**Driver dashboard shows "pending verification" instead of the toggle**
New driver accounts must be approved by an admin. Log in as admin, go to the Admin Dashboard, and click **Verify** next to the driver's name.

**Eventlet deprecation warning in the terminal**
This is a warning, not an error — the app runs fine. You can safely ignore it during development.

---

## Team Members

| # | Member | Main Area | Key Files |
|---|--------|-----------|-----------|
| 1 | Nkem Jeferon Achia | Project Lead & Architecture | `app.py`, `extensions.py`, `config/`, `README.md` |
| 2 | *(Add name)* | Database | All `models/*.py` files |
| 3 | *(Add name)* | Auth & Admin | `routes/auth.py`, `routes/admin.py`, login/register/admin templates |
| 4 | *(Add name)* | Customer Backend | `routes/customer.py`, `routes/booking.py` |
| 5 | *(Add name)* | Customer Frontend | `templates/customer_dashboard.html`, `booking.js`, `dashboard.js`, `auth.js` |
| 6 | *(Add name)* | Driver Dashboard | `routes/driver.py`, `driver_dashboard.html`, `driver_job.html` |
| 7 | *(Add name)* | Tracking, Payments & CSS | `routes/tracking.py`, `routes/payment.py`, `track_booking.html`, `tracking.js`, `style.css` |

---

## License

This project was built as an academic project for Trimester 4.
