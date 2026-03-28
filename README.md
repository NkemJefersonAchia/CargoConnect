# CargoConnect

A full-stack logistics and relocation web platform built for **Kigali, Rwanda**.
CargoConnect connects customers who need to move cargo or relocate with verified truck drivers, in real time.

---

## Demo Video

Watch the full walkthrough of CargoConnect in action:

[![CargoConnect Demo](https://img.youtube.com/vi/2BOPISW0x-o/0.jpg)](https://youtu.be/2BOPISW0x-o?si=EnjNWtuy5CAb8ZBl)

> Click the thumbnail above or [open on YouTube](https://youtu.be/2BOPISW0x-o?si=EnjNWtuy5CAb8ZBl)

---

## Table of Contents

- [What is CargoConnect?](#what-is-cargoconnect)
- [How it Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database](#database)
- [Setting Up Aiven (New Team Members)](#setting-up-aiven-new-team-members)
- [Requirements](#requirements)
- [Setup on macOS](#setup-on-macos)
- [Setup on Windows](#setup-on-windows)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Creating an Admin Account](#creating-an-admin-account)
- [Seed Data](#seed-data)
- [All Routes](#all-routes)
- [API Overview](#api-overview)
- [Socket.IO Events](#socketio-events)
- [Recent Changes](#recent-changes)
- [Common Issues](#common-issues)
- [Team Members](#team-members)

---

## What is CargoConnect?

CargoConnect is a web application that makes it easy to book a truck for moving cargo, furniture, or household goods around Kigali. Think of it like Uber but for trucks and cargo.

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
- Register and log in securely (passwords are bcrypt hashed, never stored as plain text)
- Dashboard with live stats: total bookings, completed trips, pending bookings, total spent in RWF
- Book a truck by searching by cargo weight, pickup/dropoff address, and preferred date/time
- Smart driver matching sorted by rating, with estimated cost shown upfront
  - Cost formula: `2,000 RWF base fare + 500 RWF per ton + 200 RWF per km`
- Live GPS tracking of the driver on an interactive map with no page refresh needed
- View full booking history with colour-coded status badges
- Receive in-app notifications (booking confirmed, trip completed, payment updates) with mark-as-read
- Rate the driver 1-5 stars after a completed trip with an optional written comment
- Profile section showing account name, email, and phone

### Driver
- Register with a licence number (account waits for admin verification before going live)
- Go online/offline with a large toggle switch on the dashboard
- See incoming job requests with customer details and estimated earnings
- Accept or decline individual jobs with one click
- Share live GPS location to the customer using the browser's geolocation API
- Mark trip as completed to trigger the payment flow
- **Earnings trend chart** showing weekly earnings (RWF) and job counts over the last 8 weeks, rendered as a combined bar + line chart using Chart.js
- View job history with past earnings and ratings received
- My Truck section showing registered truck plate and capacity
- Profile section showing licence, rating, and verification status

### Admin
- Full control dashboard with 6 platform-wide statistics cards
- Driver verification queue to approve or reject new driver applications
- Manage all users: search in real time by name/email/role, delete accounts
- Manage all drivers: toggle availability, remove verification, delete records
- View and filter all bookings by status (pending / confirmed / completed / cancelled)
- Full booking detail modal showing payment and trip information

### Payment (MTN MoMo)
- Payment initiated via the MTN Mobile Money sandbox Collections API
- Customer receives a payment prompt directly on their phone
- Webhook callback automatically updates the payment record in the database
- Both customer and driver are notified on payment success or failure
- If the MoMo API is unreachable, the payment stays pending and a retry notification is sent
- A local payment simulation mode is available for development and testing without a live MoMo key

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
| Web framework | Flask | Lightweight and unopinionated |
| Real-time | Flask-SocketIO + eventlet | WebSocket support for live GPS without polling |
| Database | PostgreSQL (hosted on Aiven) | Reliable, production-grade, accessible to the whole team |
| ORM | SQLAlchemy + Flask-SQLAlchemy | Clean Python objects instead of raw SQL |
| Schema migrations | Flask-Migrate (Alembic) | Safe, versioned database schema changes |
| Auth | Flask-Login + Flask-Bcrypt | Session management and industry-standard password hashing |
| Frontend | Vanilla HTML5, CSS3, JavaScript | No framework overhead |
| Maps | Leaflet.js + OpenStreetMap | Free, open-source, works well for Kigali |
| Payments | MTN MoMo Collections API | The dominant mobile money platform in Rwanda |
| Fonts | Google Fonts (Syne + DM Sans) | Clean, modern typography |
| Version control | Git + GitHub | Collaboration and full code history |

---

## Project Structure

```
CargoConnect/
|
|-- app.py                  # Entry point. Creates the Flask app and starts the server
|-- extensions.py           # Shared Flask extensions (db, bcrypt, socketio, migrate, login)
|-- seed.py                 # Script to populate the database with demo drivers
|-- seed_ola.py             # Script to populate the database with data for driver Ola
|-- requirements.txt        # All Python packages the app needs
|-- .env                    # Your secret config. Never commit this file
|-- .env.example            # Safe template showing what variables are needed
|-- ca.pem                  # SSL certificate required to connect to Aiven PostgreSQL
|
|-- config/
|   `-- config.py           # Reads .env and applies settings to the Flask app
|
|-- models/                 # Database tables defined as Python classes (SQLAlchemy ORM)
|   |-- __init__.py         # Imports db from extensions
|   |-- user.py             # users table. One row per account, shared across all roles
|   |-- customer.py         # customers table. Extra profile info for customer accounts
|   |-- driver.py           # drivers table. Licence, rating, GPS coordinates, availability
|   |-- truck.py            # trucks table. Truck plate and capacity, linked to a driver
|   |-- booking.py          # bookings table. A trip from pickup to dropoff
|   |-- payment.py          # payments table. One payment record per booking
|   |-- rating.py           # ratings table. Star rating submitted after a trip
|   `-- notification.py     # notifications table. In-app messages for any user
|
|-- routes/                 # URL handlers grouped into Flask Blueprints
|   |-- __init__.py
|   |-- auth.py             # /auth -- login, register, logout
|   |-- booking.py          # /booking -- search for drivers, create/cancel bookings
|   |-- driver.py           # /driver -- availability toggle, accept/decline/complete jobs
|   |-- customer.py         # /customer -- dashboard stats, bookings, notifications, ratings
|   |-- tracking.py         # (root) -- live tracking page and Socket.IO GPS events
|   |-- payment.py          # /payment -- MTN MoMo initiation and callback
|   `-- admin.py            # /admin -- all admin management endpoints
|
|-- templates/              # HTML pages rendered by Flask using Jinja2 templating
|   |-- base.html                 # Shared layout: sidebar, topbar, flash messages
|   |-- login.html                # Login form
|   |-- register.html             # Registration form with customer/driver role toggle
|   |-- customer_dashboard.html   # Customer home: stats, bookings, notifications, profile
|   |-- book_truck.html           # Standalone truck search page
|   |-- track_booking.html        # Live Leaflet map for tracking a trip
|   |-- driver_dashboard.html     # Driver home: jobs, truck info, profile
|   |-- driver_job.html           # Active job detail with GPS share and complete buttons
|   |-- admin_dashboard.html      # Admin overview with verification queue
|   |-- admin_users.html          # User management table with live search
|   |-- admin_drivers.html        # Driver management table
|   `-- admin_bookings.html       # Bookings table with status filter
|
`-- static/
    |-- css/
    |   `-- style.css       # All styles. Every colour and size is a CSS variable
    `-- js/
        |-- auth.js         # Role toggle on register form; auto-dismiss flash messages
        |-- booking.js      # Customer dashboard: stats, bookings, truck search, notifications
        |-- tracking.js     # Leaflet map setup and Socket.IO live location listener
        |-- dashboard.js    # Sidebar hamburger for mobile; shared formatRWF/formatDate helpers
        `-- admin.js        # Admin table utilities and confirmation modals
```

---

## Database

The database for this project is hosted on **Aiven**, a managed cloud PostgreSQL service. You do not need to install or run PostgreSQL locally. The database is shared across all team members and is always accessible as long as you have the correct credentials.

### What you need to connect

To run the app, your `.env` file must have the following values. Ask the project lead for these:

```
DATABASE_URL=postgresql://avnadmin:PASSWORD@HOST:PORT/defaultdb?sslmode=require
PGSSLROOTCERT=ca.pem
```

You also need the `ca.pem` file in the root of the project. This is the SSL certificate Aiven requires. It is not committed to the repo because it is a security file. Ask the project lead to share it with you directly.

### Aiven connection details

| Field | Value |
|-------|-------|
| Host | pg-2b4808d0-alustudent-792a.i.aivencloud.com |
| Port | 22910 |
| Database | defaultdb |
| User | avnadmin |
| SSL mode | require |

The password is shared privately. Do not commit it to GitHub.

### If you want to explore the database directly

You can connect using any PostgreSQL client (TablePlus, DBeaver, psql) with the credentials above and the `ca.pem` file set as the SSL root certificate.

Using psql from the terminal:

```bash
PGPASSWORD=YOUR_PASSWORD psql "postgresql://avnadmin@pg-2b4808d0-alustudent-792a.i.aivencloud.com:22910/defaultdb?sslmode=require&sslrootcert=ca.pem"
```

### To promote a user to admin via Aiven

```bash
PGPASSWORD=YOUR_PASSWORD psql "postgresql://avnadmin@pg-2b4808d0-alustudent-792a.i.aivencloud.com:22910/defaultdb?sslmode=require&sslrootcert=ca.pem" \
  -c "UPDATE users SET role = 'admin' WHERE user_email = 'your@email.com';"
```

---

## Setting Up Aiven (New Team Members)

If you are a new team member who needs to connect to the CargoConnect cloud database, follow these steps. You do **not** need to create your own Aiven account — the database already exists and is shared. You only need the credentials.

### Step 1 — Get the credentials from the project lead

Ask the project lead (Nkem) for:
- The `DATABASE_URL` (full PostgreSQL connection string including password)
- The `ca.pem` SSL certificate file

These are never committed to GitHub for security reasons.

### Step 2 — Sign up for Aiven (optional, only if you need your own instance)

If for any reason you need to host your own PostgreSQL instance on Aiven:

1. Go to **[aiven.io](https://aiven.io)** and click **Sign Up**
2. Create a free account using your email
3. Once logged in, click **Create Service**
4. Choose **PostgreSQL**
5. Select the **Free tier** (Hobbyist plan)
6. Choose region **Google Cloud — Iowa (us-central1)** or the one closest to you
7. Click **Create Service** and wait about 1–2 minutes for it to provision
8. Once it is running, go to the **Overview** tab of your service
9. Under **Connection Information**, copy the **Service URI** — this is your `DATABASE_URL`
10. Under **SSL**, download the **CA Certificate** — this is your `ca.pem`
11. Place `ca.pem` in the root of the project folder
12. Paste the Service URI into your `.env` as `DATABASE_URL=...`

> **Important:** The free tier expires after 30 days. For a shared team project, always use the existing hosted instance provided by the project lead.

### Step 3 — Configure your `.env`

```env
DATABASE_URL=postgresql://avnadmin:PASSWORD@HOST:PORT/defaultdb?sslmode=require
PGSSLROOTCERT=ca.pem
```

### Step 4 — Verify the connection

Start the app with `python3 app.py`. If the database connects successfully you will see:

```
wsgi starting up on http://0.0.0.0:5000
```

If you see a connection error, double-check that `ca.pem` is in the project root and that the password in `DATABASE_URL` is correct.

---

## Requirements

Make sure the following are installed on your computer before you start.

| Tool | Minimum Version | Download Link |
|------|----------------|---------------|
| Python | 3.10 | python.org/downloads |
| Git | Any recent | git-scm.com |

You do **not** need to install PostgreSQL locally. The database runs on Aiven.

---

## Setup on macOS

Follow every step in order.

### Step 1 -- Clone the project

Open Terminal and run:

```bash
git clone https://github.com/NkemJefersonAchia/CargoConnect.git
cd CargoConnect
```

### Step 2 -- Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt should now start with `(venv)`.

### Step 3 -- Install all Python packages

```bash
pip install -r requirements.txt
```

### Step 4 -- Set up your environment file

```bash
cp .env.example .env
```

Open `.env` and fill in the Aiven credentials shared by the project lead:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://avnadmin:PASSWORD@pg-2b4808d0-alustudent-792a.i.aivencloud.com:22910/defaultdb?sslmode=require
PGSSLROOTCERT=ca.pem
```

### Step 5 -- Add the SSL certificate

Place the `ca.pem` file (shared by the project lead) in the root of the project folder, at the same level as `app.py`.

### Step 6 -- Start the app

```bash
python3 app.py
```

When you see this line, the app is ready:

```
wsgi starting up on http://0.0.0.0:5000
```

Open your browser and go to: **http://localhost:5000**

To stop the app: press `Ctrl + C`.

---

## Setup on Windows

### Step 1 -- Clone the project

```cmd
git clone https://github.com/NkemJefersonAchia/CargoConnect.git
cd CargoConnect
```

### Step 2 -- Create a virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3 -- Install all Python packages

```cmd
pip install -r requirements.txt
```

### Step 4 -- Set up your environment file

```cmd
copy .env.example .env
```

Open `.env` and fill in the Aiven credentials shared by the project lead:

```env
SECRET_KEY=any-random-string-you-make-up
DATABASE_URL=postgresql://avnadmin:PASSWORD@pg-2b4808d0-alustudent-792a.i.aivencloud.com:22910/defaultdb?sslmode=require
PGSSLROOTCERT=ca.pem
```

### Step 5 -- Add the SSL certificate

Place the `ca.pem` file (shared by the project lead) in the root of the project folder, at the same level as `app.py`.

### Step 6 -- Start the app

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
| `DATABASE_URL` | Aiven PostgreSQL connection string | see Database section above |
| `PGSSLROOTCERT` | Path to the Aiven SSL certificate | `ca.pem` |
| `MOMO_API_KEY` | MTN MoMo sandbox API key | from sandbox.momodeveloper.mtn.com |
| `MOMO_USER_ID` | MTN MoMo sandbox user ID | from sandbox.momodeveloper.mtn.com |
| `MOMO_BASE_URL` | MoMo API server address | `https://sandbox.momodeveloper.mtn.com` |
| `MOMO_SUBSCRIPTION_KEY` | MoMo subscription key | from sandbox.momodeveloper.mtn.com |
| `FLASK_ENV` | Set to `development` while building | `development` |
| `FLASK_DEBUG` | Set to `1` to see detailed error pages in browser | `1` |

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

**Step 2:** Connect to Aiven and run the SQL below (replace the email):

```bash
PGPASSWORD=YOUR_PASSWORD psql "postgresql://avnadmin@pg-2b4808d0-alustudent-792a.i.aivencloud.com:22910/defaultdb?sslmode=require&sslrootcert=ca.pem" \
  -c "UPDATE users SET role = 'admin' WHERE user_email = 'your@email.com';"
```

**Step 3:** Log out and log back in. You will see the Admin Dashboard.

---

## Seed Data

The project includes a `seed.py` script that populates the database with 25 demo drivers placed across real Kigali neighbourhoods (Kimihurura, Kacyiru, Remera, Nyamirambo, and others). Each driver has a verified status, a registered truck, and realistic GPS coordinates so they appear on the booking search map.

To run the seed script:

```bash
python3 seed.py
```

This is safe to run multiple times. It uses `ON CONFLICT DO NOTHING` so it will not create duplicates.

The seed drivers use the licence format `RW-DL-XXXXXX` and are attached to user accounts with randomly generated names and phone numbers. These accounts exist only for demonstration and testing.

---

## All Routes

### Page Routes (render HTML)

| Method | URL | Template | Who can access |
|--------|-----|----------|----------------|
| GET/POST | `/auth/login` | `login.html` | Anyone |
| GET/POST | `/auth/register` | `register.html` | Anyone |
| GET | `/auth/logout` | redirect | Logged-in users |
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
| My Bookings | `#recent` | Recent bookings table |
| Book a Truck | `#quickbook` | Booking search form |
| Notifications | `#notifications` | Unread notifications list |
| My Profile | `#profile` | Account info section |

### Driver Sidebar Navigation

| Link | Destination | What it shows |
|------|------------|---------------|
| Dashboard | `/driver/dashboard` | Full dashboard page |
| My Jobs | `#jobs` | Incoming job requests |
| My Truck | `#truck` | Truck plate and capacity |
| Earnings Trend | `#earningsChart` | Weekly earnings bar + line chart (last 8 weeks) |
| Job History | `#history` | Completed jobs table with earnings and ratings |
| My Profile | `#profile` | Driver account info |

---

## API Overview

Every API endpoint returns JSON in this shape:

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
| GET | `/customer/active-booking` | Current confirmed booking if any |
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
| GET | `/driver/active-job` | Current confirmed job if any |
| POST | `/driver/job/<id>/accept` | Accept a pending booking |
| POST | `/driver/job/<id>/decline` | Decline a pending booking |
| POST | `/driver/job/<id>/complete` | Mark a confirmed trip as completed |
| GET | `/driver/job-history` | Last 10 completed jobs |
| GET | `/driver/earnings-trend` | Weekly earnings and job counts for the last 8 weeks |

### Payments (`/payment`)

| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/payment/initiate/<id>` | Initiate MTN MoMo payment for a booking |
| POST | `/payment/callback` | MoMo webhook that updates payment status |

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
| GET | `/admin/bookings` | All bookings. Add `?status=pending` to filter |

---

## Socket.IO Events

| Event name | Direction | What it does |
|-----------|-----------|-------------|
| `join_tracking_room` | Customer to Server | Customer joins the live tracking room for their booking |
| `driver_location_update` | Driver to Server | Driver sends GPS coordinates to the server |
| `location_update` | Server to Customer | Server broadcasts new driver coordinates to the customer's map |
| `joined` | Server to Customer | Confirmation that the customer joined the room |

---

## Recent Changes

This section documents all major changes made to the project since the initial build.

### Database migrated to Aiven (cloud PostgreSQL)

The database was moved from a local PostgreSQL installation to a managed cloud instance on Aiven. This means all team members connect to the same live database without needing PostgreSQL installed on their machines. The connection requires the `ca.pem` SSL certificate file and the `PGSSLROOTCERT` environment variable in `.env`.

All existing data (users, customers, drivers, trucks, bookings, notifications, payments) was migrated from the local database to Aiven during the move. The migration handled column name differences between the old local schema and the current SQLAlchemy model definitions.

### 25 seed drivers added

A `seed.py` script was created and run to populate the database with 25 verified demo drivers spread across Kigali. Each driver has a registered truck and realistic GPS coordinates. This ensures that when a customer searches for a truck, drivers appear in the results.

### Driver search fixed

The booking search endpoint (`/booking/search`) was returning no results because drivers had no GPS coordinates set. The seed data fixes this. Drivers now appear when a customer searches from any Kigali address.

### MTN MoMo simulation

The payment flow includes a simulation mode for development. When real MoMo credentials are not configured, the app simulates a successful payment and marks the booking as paid. This allows the full booking and payment flow to be tested without a live MoMo sandbox account.

### Driver earnings trend chart

A weekly earnings chart was added to the driver dashboard using **Chart.js 4**. The chart displays two datasets — a bar series for total RWF earned and a line series for job count — over the last 8 calendar weeks. It is powered by a new `/driver/earnings-trend` API endpoint that groups completed bookings by Monday-aligned calendar week and sums their `estimated_cost`. The chart renders in a 260 px tall canvas between the stat cards and the job history table.

### Seed data for driver Ola

A `seed_ola.py` script was added to populate the database with realistic test data for a single named driver. Running it creates driver **Ola Ndayisaba** (verified, available, licence `RW-DL-2021-0042`, truck `RAC 042 B`), four customer accounts, and 54 completed bookings spread across 12 weeks with payments and ratings. This gives the earnings chart real data to display immediately after seeding.

To run:

```bash
python3 seed_ola.py
```

Login credentials after seeding: `ola.ndayisaba@cargoconnect.rw` / `password123`

### `.env` and `ca.pem` added to `.gitignore`

Neither the `.env` file nor the `ca.pem` certificate are committed to the repository. Both contain credentials and must be shared privately between team members.

---

## Common Issues

**App cannot connect to the database on startup**
Check that your `.env` has the correct `DATABASE_URL` pointing to Aiven and that the `ca.pem` file is in the project root. The `PGSSLROOTCERT=ca.pem` line must also be present in `.env`.

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment is not active. Run `source venv/bin/activate` on macOS or `venv\Scripts\activate` on Windows.

**`Address already in use` on port 5000**
Something else is using port 5000. On macOS, AirPlay Receiver commonly causes this. Go to System Settings, then General, then AirDrop and Handoff, and turn AirPlay Receiver off. Or change the port in `app.py`:

```python
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```

Then visit http://localhost:5001.

**No drivers appear when searching for a truck**
The seed data may not have been loaded into the database. Ask the project lead to confirm it was run, or run `python3 seed.py` yourself if you have write access to the database.

**Driver dashboard shows "pending verification" instead of the toggle**
New driver accounts must be approved by an admin. Log in as admin, go to the Admin Dashboard, and click Verify next to the driver's name.

**Eventlet deprecation warning in the terminal**
This is a warning, not an error. The app runs fine. You can safely ignore it during development.

**SSL error when connecting to the database**
Make sure `ca.pem` is in the project root and that `PGSSLROOTCERT=ca.pem` is in your `.env`. The certificate must match exactly the one provided by Aiven for the hosted instance.

---

## Team Members

| # | Member | Main Area | Key Files |
|---|--------|-----------|-----------|
| 1 | Nkem Jeferson Achia | Project Lead and Architecture | `app.py`, `extensions.py`, `config/`, `README.md` |
| 2 | *(Add name)* | Database | All `models/*.py` files |
| 3 | *(Add name)* | Auth and Admin | `routes/auth.py`, `routes/admin.py`, login/register/admin templates |
| 4 | *(Add name)* | Customer Backend | `routes/customer.py`, `routes/booking.py` |
| 5 | *(Add name)* | Customer Frontend | `templates/customer_dashboard.html`, `booking.js`, `dashboard.js`, `auth.js` |
| 6 | *(Add name)* | Driver Dashboard | `routes/driver.py`, `driver_dashboard.html`, `driver_job.html` |
| 7 | *(Add name)* | Tracking, Payments and CSS | `routes/tracking.py`, `routes/payment.py`, `track_booking.html`, `tracking.js`, `style.css` |

---

## License

This project was built as an academic project for Trimester 4 at the African Leadership University.
