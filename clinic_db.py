import sqlite3
from datetime import date, timedelta, datetime
from pathlib import Path


# Keep the database inside the project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "clinic.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the table and ensure demo slots exist for tomorrow."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available'
                    CHECK (status IN ('available', 'booked')),
                UNIQUE (appointment_date, appointment_time, doctor_name)
            )
        """)

        # Safely add patient fields to an existing database
        existing_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(appointments)").fetchall()
        }

        if "patient_name" not in existing_columns:
            conn.execute("ALTER TABLE appointments ADD COLUMN patient_name TEXT")

        if "patient_phone" not in existing_columns:
            conn.execute("ALTER TABLE appointments ADD COLUMN patient_phone TEXT")

        # Add tomorrow's demo slots every time initialization runs.
        # INSERT OR IGNORE keeps existing records/bookings and avoids duplicates.
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        demo_slots = [
            (tomorrow, "10:00", "Dr. Ahmed", "available"),
            (tomorrow, "11:00", "Dr. Ahmed", "available"),
            (tomorrow, "12:00", "Dr. Ahmed", "booked"),
            (tomorrow, "17:00", "Dr. Ahmed", "available"),
            (tomorrow, "18:00", "Dr. Sara", "available"),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO appointments
            (appointment_date, appointment_time, doctor_name, status)
            VALUES (?, ?, ?, ?)
        """, demo_slots)

    print(f"Database initialized: {DB_PATH}")


def check_availability(appointment_date, doctor_name=None):
    """Return available appointment slots for a given date."""
    query = """
        SELECT appointment_time, doctor_name
        FROM appointments
        WHERE appointment_date = ?
          AND status = 'available'
    """
    params = [appointment_date]

    if doctor_name:
        query += " AND doctor_name = ?"
        params.append(doctor_name)

    query += " ORDER BY appointment_time"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [{"time": time, "doctor": doctor} for time, doctor in rows]


def book_appointment(
    appointment_date,
    appointment_time,
    doctor_name,
    patient_name,
    patient_phone,
):
    """Book an existing available appointment safely."""
    patient_name = patient_name.strip()
    patient_phone = patient_phone.strip()
    doctor_name = doctor_name.strip()
    appointment_time = appointment_time.strip()

    if not all([
        appointment_date,
        appointment_time,
        doctor_name,
        patient_name,
        patient_phone,
    ]):
        return {
            "success": False,
            "message": "All booking details are required.",
        }

    try:
        parsed_date = date.fromisoformat(appointment_date)
        datetime.strptime(appointment_time, "%H:%M")
    except ValueError:
        return {
            "success": False,
            "message": "Invalid date or time format.",
        }

    if parsed_date < date.today():
        return {
            "success": False,
            "message": "Cannot book an appointment in the past.",
        }

    with get_connection() as conn:
        # Lock the write transaction to prevent double booking.
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            """
            SELECT id, status
            FROM appointments
            WHERE appointment_date = ?
              AND appointment_time = ?
              AND doctor_name = ?
            """,
            (parsed_date.isoformat(), appointment_time, doctor_name),
        ).fetchone()

        if row is None:
            return {
                "success": False,
                "message": "This appointment slot does not exist.",
            }

        if row[1] != "available":
            return {
                "success": False,
                "message": "This appointment is no longer available.",
            }

        cursor = conn.execute(
            """
            UPDATE appointments
            SET status = 'booked',
                patient_name = ?,
                patient_phone = ?
            WHERE id = ?
              AND status = 'available'
            """,
            (patient_name, patient_phone, row[0]),
        )

        if cursor.rowcount != 1:
            return {
                "success": False,
                "message": "This appointment is no longer available.",
            }

    return {
        "success": True,
        "message": "Appointment booked successfully.",
        "date": parsed_date.isoformat(),
        "time": appointment_time,
        "doctor": doctor_name,
        "patient_name": patient_name,
    }


if __name__ == "__main__":
    initialize_database()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    slots = check_availability(tomorrow)

    print(f"\nAvailable appointments for tomorrow ({tomorrow}):")
    for slot in slots:
        print(f"{slot['time']} - {slot['doctor']}")

    if not slots:
        print("No available appointments.")
