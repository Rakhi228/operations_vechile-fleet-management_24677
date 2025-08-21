backend_fin.py

import psycopg2
from psycopg2 import sql
import os

# Database connection details
DB_NAME = "Vehicle_fleet_management"
DB_USER = "postgres"
DB_PASS = "Rakhi@224"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table():
    """Creates the vehicles table if it doesn't exist."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id VARCHAR(255) PRIMARY KEY,
                    make VARCHAR(50) NOT NULL,
                    model VARCHAR(50),
                    status VARCHAR(50),
                    current_mileage INTEGER,
                    last_service_date DATE
                );
            """)
        conn.commit()
        conn.close()

# --- CRUD Operations ---

def create_vehicle(vehicle_id, make, model, status, current_mileage, last_service_date):
    """Inserts a new vehicle record into the database."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vehicles (vehicle_id, make, model, status, current_mileage, last_service_date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (vehicle_id, make, model, status, current_mileage, last_service_date))
        conn.commit()
        conn.close()

def read_vehicles(filter_by=None, filter_value=None, sort_by=None, sort_order='ASC'):
    """
    Reads vehicle records from the database with optional filtering and sorting.
    """
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM vehicles"
            params = []
            
            # Filtering Logic
            if filter_by and filter_value:
                query += f" WHERE {filter_by} = %s"
                params.append(filter_value)
            
            # Sorting Logic
            if sort_by:
                if sort_by == 'current_mileage':
                    query += " ORDER BY current_mileage DESC"
                elif sort_by == 'last_service_date':
                    query += " ORDER BY last_service_date ASC"

            cur.execute(query, params)
            vehicles = cur.fetchall()
            conn.close()
            return vehicles
    return []

def update_vehicle(vehicle_id, make, model, status, current_mileage, last_service_date):
    """Updates an existing vehicle record."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE vehicles SET make = %s, model = %s, status = %s, current_mileage = %s, last_service_date = %s
                WHERE vehicle_id = %s;
            """, (make, model, status, current_mileage, last_service_date, vehicle_id))
        conn.commit()
        conn.close()

def delete_vehicle(vehicle_id):
    """Deletes a vehicle record from the database."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vehicles WHERE vehicle_id = %s;", (vehicle_id,))
        conn.commit()
        conn.close()

# --- Aggregation and Business Insights ---

def get_fleet_insights():
    """
    Retrieves aggregated business insights for the vehicle fleet.
    """
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # COUNT & AVG
            cur.execute("SELECT COUNT(*) FROM vehicles;")
            total_vehicles = cur.fetchone()[0]

            cur.execute("SELECT AVG(current_mileage) FROM vehicles;")
            avg_mileage = cur.fetchone()[0]

            # MAX & MIN Mileage vehicles
            cur.execute("SELECT vehicle_id, current_mileage, make FROM vehicles WHERE current_mileage = (SELECT MAX(current_mileage) FROM vehicles);")
            max_mileage_vehicle = cur.fetchone()

            cur.execute("SELECT vehicle_id, current_mileage, make FROM vehicles WHERE current_mileage = (SELECT MIN(current_mileage) FROM vehicles);")
            min_mileage_vehicle = cur.fetchone()

            conn.close()
            return {
                "total_vehicles": total_vehicles,
                "avg_mileage": avg_mileage,
                "max_mileage_vehicle": max_mileage_vehicle,
                "min_mileage_vehicle": min_mileage_vehicle
            }
    return {}

# --- Helper Functions for Streamlit UI ---

def get_unique_values(column_name):
    """Fetches unique values for a given column (e.g., 'make' or 'status')."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT DISTINCT {} FROM vehicles;").format(sql.Identifier(column_name)))
            values = [row[0] for row in cur.fetchall()]
            conn.close()
            return values
    return []
