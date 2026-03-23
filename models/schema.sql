-- =============================================================================
-- CargoConnect Database Schema
-- PostgreSQL 14+
-- All ERD faults corrected (see comments where fixes were applied)
-- =============================================================================

-- Run this file with:
--   psql -U postgres -d cargoconnect -f cargoconnect_schema.sql
-- Or from within psql:
--   \i cargoconnect_schema.sql

-- Drop tables in reverse dependency order (safe re-run)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS trucks CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop custom ENUM types if they exist (for clean re-runs)
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS booking_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;


-- =============================================================================
-- ENUM TYPES
-- =============================================================================

CREATE TYPE user_role AS ENUM ('customer', 'driver', 'admin');

CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'completed', 'cancelled');

CREATE TYPE payment_status AS ENUM ('pending', 'success', 'failed');


-- =============================================================================
-- TABLE: users
-- Central account table shared by all roles.
-- FIX #3: Corrected VRCHAR typo → VARCHAR on user_name and user_email
-- =============================================================================

CREATE TABLE users (
    user_id         SERIAL          PRIMARY KEY,
    user_name       VARCHAR(100)    NOT NULL,                        -- FIX: was VRCHAR(100)
    user_email      VARCHAR(200)    NOT NULL UNIQUE,                 -- FIX: was VRCHAR(200), added UNIQUE
    password_hash   VARCHAR(250)    NOT NULL,
    user_phone_no   VARCHAR(20)     NOT NULL,                        -- FIX: gave it a sensible length
    role            user_role       NOT NULL DEFAULT 'customer',
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- Index for fast login lookups by email
CREATE INDEX idx_users_email ON users (user_email);
CREATE INDEX idx_users_role  ON users (role);


-- =============================================================================
-- TABLE: customers
-- Extra profile data for customer accounts.
-- =============================================================================

CREATE TABLE customers (
    customer_id     SERIAL          PRIMARY KEY,
    user_id         INT             NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    default_address TEXT
);


-- =============================================================================
-- TABLE: drivers
-- FIX #5: Added licence_no, is_verified, latitude, longitude — all missing from ERD
-- =============================================================================

CREATE TABLE drivers (
    driver_id       SERIAL          PRIMARY KEY,
    user_id         INT             NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    licence_no      VARCHAR(50)     NOT NULL UNIQUE,                 -- FIX: was missing entirely
    rating          FLOAT           NOT NULL DEFAULT 5.0,            -- Denormalized avg, updated on each new rating
    availability    BOOLEAN         NOT NULL DEFAULT FALSE,
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE,          -- FIX: was missing — drives admin approval flow
    latitude        FLOAT,                                           -- FIX: was missing — needed for Haversine matching
    longitude       FLOAT,                                           -- FIX: was missing — needed for Haversine matching
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_drivers_verified_available ON drivers (is_verified, availability);


-- =============================================================================
-- TABLE: trucks
-- FIX #2: plate_no corrected from INT → VARCHAR (plate numbers are alphanumeric)
-- =============================================================================

CREATE TABLE trucks (
    truck_id        SERIAL          PRIMARY KEY,
    driver_id       INT             NOT NULL REFERENCES drivers(driver_id) ON DELETE CASCADE,
    plate_no        VARCHAR(20)     NOT NULL UNIQUE,                 -- FIX: was INT — Rwandan plates are e.g. "RAD 123 A"
    capacity        FLOAT           NOT NULL                         -- Capacity in tons
);


-- =============================================================================
-- TABLE: bookings
-- FIX #1: estimated_cost corrected from VARCHAR(200) → DECIMAL(10,2)
-- FIX #4: dropoff_address corrected from "drop_off_adrdess" typo
-- FIX #8: Added cargo_weight (needed for cost formula and fare auditing)
-- =============================================================================

CREATE TABLE bookings (
    booking_id      SERIAL              PRIMARY KEY,
    customer_id     INT                 NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    driver_id       INT                 REFERENCES drivers(driver_id) ON DELETE SET NULL,
    truck_id        INT                 REFERENCES trucks(truck_id) ON DELETE SET NULL,
    pickup_address  TEXT                NOT NULL,
    dropoff_address TEXT                NOT NULL,                    -- FIX: was "drop_off_adrdess" (typo)
    cargo_weight    FLOAT               NOT NULL,                    -- FIX: was missing — required for 500 RWF/ton formula
    estimated_cost  DECIMAL(10, 2)      NOT NULL,                    -- FIX: was VARCHAR(200) — must be numeric
    scheduled_time  TIMESTAMP           NOT NULL,
    status          booking_status      NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP           NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bookings_customer ON bookings (customer_id);
CREATE INDEX idx_bookings_driver   ON bookings (driver_id);
CREATE INDEX idx_bookings_status   ON bookings (status);


-- =============================================================================
-- TABLE: payments
-- FIX #6: Added momo_reference_id — required for MTN MoMo webhook callback matching
-- =============================================================================

CREATE TABLE payments (
    payment_id          SERIAL          PRIMARY KEY,
    booking_id          INT             NOT NULL UNIQUE REFERENCES bookings(booking_id) ON DELETE RESTRICT,
    amount              DECIMAL(10, 2)  NOT NULL,
    method              VARCHAR(50)     NOT NULL DEFAULT 'MTN_MOMO',
    status              payment_status  NOT NULL DEFAULT 'pending',
    momo_reference_id   VARCHAR(100),                               -- FIX: was missing — MoMo API returns this on initiation
    paid_at             TIMESTAMP                                    -- NULL until payment succeeds
);


-- =============================================================================
-- TABLE: ratings
-- FIX #10: Added UNIQUE constraint on (booking_id, customer_id) — prevents double-rating
-- =============================================================================

CREATE TABLE ratings (
    rating_id       SERIAL          PRIMARY KEY,
    booking_id      INT             NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    customer_id     INT             NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    driver_id       INT             NOT NULL REFERENCES drivers(driver_id) ON DELETE CASCADE,
    rating_score    FLOAT           NOT NULL CHECK (rating_score >= 1 AND rating_score <= 5),
    comment         TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_one_rating_per_booking UNIQUE (booking_id, customer_id)   -- FIX: prevents duplicate ratings
);

CREATE INDEX idx_ratings_driver ON ratings (driver_id);


-- =============================================================================
-- TABLE: notifications
-- FIX #7: Added booking_id FK (nullable) — links notifications to specific bookings
-- =============================================================================

CREATE TABLE notifications (
    notification_id SERIAL          PRIMARY KEY,
    user_id         INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    booking_id      INT             REFERENCES bookings(booking_id) ON DELETE SET NULL, -- FIX: was missing
    message         TEXT            NOT NULL,
    channel         VARCHAR(50)     NOT NULL DEFAULT 'in_app',      -- e.g. 'in_app', 'sms'
    is_read         BOOLEAN         NOT NULL DEFAULT FALSE,
    sent_at         TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user   ON notifications (user_id);
CREATE INDEX idx_notifications_unread ON notifications (user_id, is_read) WHERE is_read = FALSE;


-- =============================================================================
-- TRIGGER: auto-update drivers.rating after each new rating insert
-- Fixes issue #9 — rating was a stale float with no sync mechanism
-- =============================================================================

CREATE OR REPLACE FUNCTION update_driver_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE drivers
    SET rating = (
        SELECT ROUND(AVG(rating_score)::NUMERIC, 2)
        FROM ratings
        WHERE driver_id = NEW.driver_id
    )
    WHERE driver_id = NEW.driver_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_driver_rating
AFTER INSERT ON ratings
FOR EACH ROW
EXECUTE FUNCTION update_driver_rating();


-- =============================================================================
-- TRIGGER: auto-update drivers.updated_at on availability/location change
-- =============================================================================

CREATE OR REPLACE FUNCTION set_driver_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_driver_updated_at
BEFORE UPDATE ON drivers
FOR EACH ROW
EXECUTE FUNCTION set_driver_updated_at();


-- =============================================================================
-- VERIFICATION QUERIES
-- Run these after the script to confirm everything was created correctly
-- =============================================================================

-- List all tables
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Check bookings columns (verify estimated_cost type and dropoff_address spelling)
-- SELECT column_name, data_type, character_maximum_length
-- FROM information_schema.columns
-- WHERE table_name = 'bookings'
-- ORDER BY ordinal_position;

-- Check drivers columns (verify is_verified, latitude, longitude, licence_no)
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'drivers'
-- ORDER BY ordinal_position;

