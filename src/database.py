import sqlite3
import os
import datetime
from typing import List, Dict, Tuple, Optional, Any, Union

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'parking.db')

def ensure_db_directory():
    """Ensure the directory for the database exists"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """Create a connection to the SQLite database"""
    ensure_db_directory()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create parking_spaces table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_spaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_number TEXT UNIQUE NOT NULL,
        location TEXT NOT NULL,
        floor TEXT,
        section TEXT,
        is_accessible BOOLEAN DEFAULT 0,
        is_ev_charging BOOLEAN DEFAULT 0,
        hourly_rate REAL NOT NULL,
        is_available BOOLEAN DEFAULT 1,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'maintenance', 'reserved', 'inactive')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        space_id INTEGER NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        vehicle_plate TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (space_id) REFERENCES parking_spaces (id)
    )
    ''')
    
    # Create payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        transaction_id TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'failed', 'refunded')),
        payment_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# ---- User CRUD Operations ----

def create_user(username: str, password: str, email: str, full_name: str, 
                phone: str = None, is_admin: bool = False) -> int:
    """Create a new user and return the user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO users (username, password, email, full_name, phone, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, email, full_name, phone, is_admin))
        
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Username or email already exists")
    finally:
        conn.close()

def get_user(user_id: int) -> Dict:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_username(username: str) -> Dict:
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def update_user(user_id: int, **kwargs) -> bool:
    """Update user information"""
    allowed_fields = ['username', 'email', 'full_name', 'phone', 'password']
    update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_data:
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)
    
    try:
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Username or email already exists")
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """Delete a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

# ---- Parking Space CRUD Operations ----

def create_parking_space(space_number: str, location: str, hourly_rate: float,
                         floor: str = None, section: str = None, 
                         is_accessible: bool = False, is_ev_charging: bool = False) -> int:
    """Create a new parking space and return the ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO parking_spaces (
            space_number, location, floor, section, 
            is_accessible, is_ev_charging, hourly_rate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (space_number, location, floor, section, is_accessible, is_ev_charging, hourly_rate))
        
        space_id = cursor.lastrowid
        conn.commit()
        return space_id
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Space number already exists")
    finally:
        conn.close()

def get_parking_space(space_id: int) -> Dict:
    """Get parking space by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM parking_spaces WHERE id = ?', (space_id,))
    space = cursor.fetchone()
    conn.close()
    
    if space:
        return dict(space)
    return None

def get_all_parking_spaces() -> List[Dict]:
    """Get all parking spaces"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM parking_spaces ORDER BY space_number')
    spaces = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return spaces

def get_available_parking_spaces() -> List[Dict]:
    """Get all available parking spaces"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM parking_spaces WHERE is_available = 1 AND status = "active" ORDER BY space_number'
    )
    spaces = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return spaces

def update_parking_space(space_id: int, **kwargs) -> bool:
    """Update parking space information"""
    allowed_fields = ['space_number', 'location', 'floor', 'section', 
                      'is_accessible', 'is_ev_charging', 'hourly_rate',
                      'is_available', 'status']
    update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_data:
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(space_id)
    
    try:
        cursor.execute(f"UPDATE parking_spaces SET {set_clause} WHERE id = ?", values)
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Space number already exists")
    finally:
        conn.close()

def delete_parking_space(space_id: int) -> bool:
    """Delete a parking space"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM parking_spaces WHERE id = ?', (space_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

# ---- Booking CRUD Operations ----

def create_booking(user_id: int, space_id: int, start_time: datetime.datetime,
                   end_time: datetime.datetime, vehicle_plate: str, 
                   vehicle_type: str) -> int:
    """Create a new booking and return the booking ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the space is available for the requested time period
    cursor.execute('''
    SELECT id FROM bookings 
    WHERE space_id = ? AND status = 'active' AND 
          ((start_time <= ? AND end_time >= ?) OR
           (start_time <= ? AND end_time >= ?) OR
           (start_time >= ? AND end_time <= ?))
    ''', (space_id, start_time, start_time, end_time, end_time, start_time, end_time))
    
    if cursor.fetchone():
        conn.close()
        raise ValueError("Parking space is not available for the requested time period")
    
    try:
        cursor.execute('''
        INSERT INTO bookings (user_id, space_id, start_time, end_time, vehicle_plate, vehicle_type)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, space_id, start_time, end_time, vehicle_plate, vehicle_type))
        
        booking_id = cursor.lastrowid
        
        # Update parking space availability
        cursor.execute('UPDATE parking_spaces SET is_available = 0 WHERE id = ?', (space_id,))
        
        conn.commit()
        return booking_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_booking(booking_id: int) -> Dict:
    """Get booking by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.*, p.space_number, p.location, p.hourly_rate,
           u.username, u.full_name, u.email, u.phone
    FROM bookings b
    JOIN parking_spaces p ON b.space_id = p.id
    JOIN users u ON b.user_id = u.id
    WHERE b.id = ?
    ''', (booking_id,))
    
    booking = cursor.fetchone()
    conn.close()
    
    if booking:
        return dict(booking)
    return None

def get_user_bookings(user_id: int) -> List[Dict]:
    """Get all bookings for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.*, p.space_number, p.location, p.hourly_rate
    FROM bookings b
    JOIN parking_spaces p ON b.space_id = p.id
    WHERE b.user_id = ?
    ORDER BY b.start_time DESC
    ''', (user_id,))
    
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return bookings

def get_active_bookings() -> List[Dict]:
    """Get all active bookings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.*, p.space_number, p.location, p.hourly_rate,
           u.username, u.full_name, u.email, u.phone
    FROM bookings b
    JOIN parking_spaces p ON b.space_id = p.id
    JOIN users u ON b.user_id = u.id
    WHERE b.status = 'active'
    ORDER BY b.start_time
    ''')
    
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return bookings

def update_booking(booking_id: int, **kwargs) -> bool:
    """Update booking information"""
    allowed_fields = ['start_time', 'end_time', 'vehicle_plate', 'vehicle_type', 'status']
    update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_data:
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(booking_id)
    
    try:
        cursor.execute(f"UPDATE bookings SET {set_clause} WHERE id = ?", values)
        
        # If status is updated to 'completed' or 'cancelled', make the space available again
        if 'status' in update_data and update_data['status'] in ('completed', 'cancelled'):
            cursor.execute('''
            UPDATE parking_spaces 
            SET is_available = 1 
            WHERE id = (SELECT space_id FROM bookings WHERE id = ?)
            ''', (booking_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_booking(booking_id: int) -> bool:
    """Delete a booking"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, get the space_id to update its availability

