import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def get_connection():
    db = mysql.connector.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    return db

def get_existing_vehicles(vehicle_codes):
    if not vehicle_codes:
        return []

    placeholders = ', '.join(['%s'] * len(vehicle_codes))

    query = f"""
        SELECT vehicle_id, 
        CONCAT(
            vehicle_make, '_', 
            vehicle_body, '_', 
            vehicle_color, '_', 
            IFNULL(vehicle_plate_expiry, '')
        ) as vehicle_code 
        FROM vehicle
        WHERE CONCAT(
            vehicle_make, '_', 
            vehicle_body, '_', 
            vehicle_color, '_', 
            IFNULL(vehicle_plate_expiry, '')
        ) IN ({placeholders})
    """
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(query, tuple(vehicle_codes))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def get_existing_violations(violation_codenames):
    if not violation_codenames:
        return []

    placeholders = ', '.join(['%s'] * len(violation_codenames))

    query = f"""
        SELECT violation_id, CONCAT(violation_code, '_', violation_state) as violation_codename
        FROM violation
        WHERE CONCAT(violation_code, '_', violation_state) IN ({placeholders})
    """
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(query, tuple(violation_codenames))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def stringify_data(data): 
    data = ', '.join(["'{}'".format(value) if value is not None else 'NULL' for value in data.values()])
    return f"({data})"

def insert_vehicles(vehicles):
    #transform all to string
    data = map(stringify_data, vehicles)

    #glue them together
    batchData = ", ".join(e for e in data)

    fieldNames = list(vehicles[0].keys())
    fields = ", ".join(e for e in fieldNames)

    query = f"""
        INSERT into vehicle ({fields}) VALUES {batchData}
    """

    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute(query, data)
        db.commit()
        print(f"{cursor.rowcount} vehicles inserted.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
    return
    
    return

def insert_violations(violations):
    #transform all to string
    data = map(stringify_data, violations)
    
    #glue them together
    batchData = ", ".join(e for e in data)

    fieldNames = list(violations[0].keys())
    fields = ", ".join(e for e in fieldNames)

    query = f"""
        INSERT into violation ({fields}) VALUES {batchData}
    """

    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute(query, data)
        db.commit()
        print(f"{cursor.rowcount} violations inserted.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
    return

def insert_tickets(tickets):
    fields = list(tickets[0].keys())
    field_names = ", ".join(e for e in fields)
    placeholders = ", ".join(["%s" if field != 'ticket_coordinates' else "ST_GeomFromText(%s)" for field in fields])

    update_columns = ", ".join([f"{field}=VALUES({field})" for field in fields if field != 'ticket_id'])
    
    query = f"""
        INSERT INTO ticket ({field_names}) VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_columns}
    """

    # since we have coordinates, we have to prepare it differently
    data = []
    for ticket in tickets:
        row = []
        for field in fields:
            if field == 'ticket_coordinates':
                lng = ticket[field]['longitude']
                lat = ticket[field]['latitude']
                row.append(f'POINT({lng} {lat})')
            else:
                row.append(ticket[field])
        data.append(tuple(row))

    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.executemany(query, data)
        db.commit()
        print(f"{cursor.rowcount} tickets inserted.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

    return
