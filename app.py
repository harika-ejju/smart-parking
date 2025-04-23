import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os
import hashlib
import json
from streamlit_option_menu import option_menu
import random

# Page configuration
# Set page title and configuration
st.set_page_config(
    page_title="The Parkmate - Smart Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Improved CSS styling for better visibility
css = """
<style>
    /* Overall text color improvement */
    body, p, label, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important; 
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        background-color: #1E3A8A;
        color: white !important;
        padding: 8px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        font-weight: 600;
        text-align: center;
    }
    
    /* Form styling */
    .form-container {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input, .stSelectbox select {
        border: 2px solid #94a3b8 !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-weight: 500;
        border-radius: 5px;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: 600;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #2563EB !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Special emphasis for important information */
    .important-info {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        color: #92400e !important;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-weight: 500;
    }
    
    /* Parking spot styling */
    .available {
        background-color: #10B981 !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 5px;
        font-weight: 600;
    }
    
    .booked {
        background-color: #EF4444 !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 5px;
        font-weight: 600;
    }
    
    .maintenance {
        background-color: #F59E0B !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 5px;
        font-weight: 600;
    }
    
    /* Bookings and History Styling */
    .booking-card {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .booking-info {
        color: #334155 !important;
        margin-bottom: 5px;
    }
    
    .booking-title {
        font-size: 18px;
        font-weight: 600;
        color: #1e293b !important;
        margin-bottom: 10px;
    }
    
    /* Table styling */
    .styled-table {
        border-collapse: collapse;
        width: 100%;
        border: 1px solid #ddd;
        font-size: 16px;
    }
    
    .styled-table th {
        background-color: #1E3A8A;
        color: white !important;
        text-align: left;
        padding: 12px;
        font-weight: 600;
    }
    
    .styled-table td {
        border: 1px solid #ddd;
        padding: 12px;
        color: #333333 !important;
    }
    
    .styled-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    .styled-table tr:hover {
        background-color: #ddd;
    }
    
    /* Authentication form */
    .auth-form {
        max-width: 500px;
        margin: 0 auto;
        padding: 25px;
        background-color: #f8fafc;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #cbd5e1;
    }
    
    /* Login/Register tabs */
    .auth-tabs {
        display: flex;
        margin-bottom: 20px;
    }
    
    .auth-tab {
        flex: 1;
        text-align: center;
        padding: 10px;
        background-color: #e2e8f0;
        color: #475569 !important;
        font-weight: 600;
        cursor: pointer;
    }
    
    .auth-tab.active {
        background-color: #1E3A8A;
        color: white !important;
    }
    
    .auth-tab:first-child {
        border-top-left-radius: 5px;
        border-bottom-left-radius: 5px;
    }
    
    .auth-tab:last-child {
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
    }
    
    /* Label styling */
    label {
        font-weight: 600;
        color: #334155 !important;
        margin-bottom: 5px;
        display: block;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# Database setup
def init_db():
    conn = None
    try:
        conn = sqlite3.connect('parking.db', check_same_thread=False)
        c = conn.cursor()
        
        # Create users table
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
        ''')
        
        # Create parking_spots table
        c.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_number TEXT,
            status TEXT,
            section TEXT,
            floor INTEGER
        )
        ''')
        
        # Create bookings table
        c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            spot_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            payment_status TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (spot_id) REFERENCES parking_spots (id)
        )
        ''')
        
        # Check if we need to create sample data
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            # Create admin user
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                     ("admin", hashed_password, "admin@example.com", 1))
            
            # Create regular user
            hashed_password = hashlib.sha256("password123".encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                     ("john_doe", hashed_password, "john@example.com", 0))
            
            # Create parking spots
            sections = ['A', 'B', 'C']
            floors = [1, 2, 3]
            for section in sections:
                for floor in floors:
                    for i in range(1, 6):
                        spot_number = f"{section}{floor}-{i}"
                        status = random.choice(['available', 'booked', 'maintenance'])
                        c.execute("INSERT INTO parking_spots (spot_number, status, section, floor) VALUES (?, ?, ?, ?)",
                                 (spot_number, status, section, floor))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()
init_db()

# Helper functions for database operations
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('parking.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        if conn:
            conn.close()
        return None

def validate_login(username, password):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                           (username, hashed_password)).fetchone()
        return user
    except Exception as e:
        st.error(f"Login validation error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def register_user(username, password, email):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, email, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_available_spots():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        spots = conn.execute("SELECT * FROM parking_spots WHERE status = 'available'").fetchall()
        return spots
    except Exception as e:
        st.error(f"Error fetching available spots: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_spots():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        spots = conn.execute("SELECT * FROM parking_spots").fetchall()
        return spots
    except Exception as e:
        st.error(f"Error fetching all spots: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user_bookings(user_id):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        bookings = conn.execute("""
        SELECT b.id, b.start_time, b.end_time, b.status, b.payment_status, p.spot_number, p.section, p.floor, b.spot_id
        FROM bookings b
        JOIN parking_spots p ON b.spot_id = p.id
        WHERE b.user_id = ?
        ORDER BY b.start_time DESC
        """, (user_id,)).fetchall()
        return bookings
    except Exception as e:
        st.error(f"Error fetching user bookings: {e}")
        return []
    finally:
        if conn:
            conn.close()

def book_spot(user_id, spot_id, start_time, end_time):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
            
        conn.execute("""
        INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, spot_id, start_time, end_time, 'confirmed', 'pending'))
        
        conn.execute("""
        UPDATE parking_spots
        SET status = 'booked'
        WHERE id = ?
        """, (spot_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error booking spot: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def cancel_booking(booking_id, spot_id):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        # Start a transaction to ensure both updates happen or none
        conn.execute("BEGIN TRANSACTION")
            
        conn.execute("""
        UPDATE bookings
        SET status = 'cancelled'
        WHERE id = ?
        """, (booking_id,))
        
        conn.execute("""
        UPDATE parking_spots
        SET status = 'available'
        WHERE id = ?
        """, (spot_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error cancelling booking: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Authentication pages
def login_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #1E3A8A;">The Parkmate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569;">Smart Parking Management System</p>', unsafe_allow_html=True)

    # Login/Register tabs
    tabs = st.tabs(["Login", "Register"])
    with tabs[0]:
        st.markdown('<div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 2px solid #cbd5e1; margin-top: 15px;">', unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username", help="Enter your registered username")
        password = st.text_input("Password", type="password", key="login_password", help="Enter your password")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Login", key="login_button"):
            if username and password:
                user = validate_login(username, password)
                if user:
                    st.session_state.user = {
                        'id': user['id'],
                        'username': user['username'],
                        'is_admin': user['is_admin']
                    }
                    st.session_state.page = "home"
                    st.experimental_rerun()
                else:
                    st.markdown('<div class="important-info">Invalid username or password</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="important-info">Please enter both username and password</div>', unsafe_allow_html=True)

    with tabs[1]:
        register_page()
    st.markdown('</div>', unsafe_allow_html=True)
# Registration page

def register_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #1E3A8A;">The Parkmate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569;">Smart Parking Management System</p>', unsafe_allow_html=True)
    
    # Register form
    st.markdown('<div class="auth-tabs"><div class="auth-tab" onclick="window.location.href=\'?page=login\'">Login</div><div class="auth-tab active">Register</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 2px solid #cbd5e1; margin-top: 15px;">', unsafe_allow_html=True)
    username = st.text_input("Username", key="reg_username", help="Choose a unique username")
    email = st.text_input("Email", key="reg_email", help="Enter a valid email address")
    password = st.text_input("Password", type="password", key="reg_password", help="Minimum 6 characters")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", help="Re-enter your password")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Use a variable to store the registration message
    registration_message = st.empty()
    
    if st.button("Register", key="register_button"):
        # Form validation
        if not username or not email or not password or not confirm_password:
            registration_message.markdown('<div class="important-info">Please fill out all fields</div>', unsafe_allow_html=True)
        elif password != confirm_password:
            registration_message.markdown('<div class="important-info">Passwords do not match</div>', unsafe_allow_html=True)
        elif len(password) < 6:
            registration_message.markdown('<div class="important-info">Password must be at least 6 characters long</div>', unsafe_allow_html=True)
        elif '@' not in email or '.' not in email:
            registration_message.markdown('<div class="important-info">Please enter a valid email address</div>', unsafe_allow_html=True)
        else:
            if register_user(username, password, email):
                registration_message.markdown('<div class="important-info" style="background-color: #d1fae5; border-left-color: #10b981; color: #065f46 !important;">Registration successful! You can now log in.</div>', unsafe_allow_html=True)
                st.success("Registration successful! Please log in.")
                # Do NOT attempt to clear st.session_state widget keys after instantiation
                # Instead, suggest the user to log in or reload the page
            else:
                registration_message.markdown('<div class="important-info">Username already exists. Please choose a different username.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
# Main application pages
def home_page():
    st.markdown('<h1 class="section-header">Welcome to The Parkmate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569; margin-bottom: 20px;">Your Smart Parking Management Solution</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="form-container">
            <h2 style="color: #1E3A8A; margin-bottom: 15px;">Parking Made Easy</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #333333;">
                Our AI-powered parking management system helps you find and book parking spots with ease.
                No more driving around in circles looking for parking spaces!
            </p>
            <ul style="margin-top: 15px; color: #333333;">
                <li style="margin-bottom: 8px;">Real-time parking availability</li>
                <li style="margin-bottom: 8px;">Book parking spots in advance</li>
                <li style="margin-bottom: 8px;">Flexible payment options</li>
                <li style="margin-bottom: 8px;">Reduced congestion and emissions</li>
                <li style="margin-bottom: 8px;">Vehicle security and monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="form-container">
            <h3 style="color: #1E3A8A; margin-bottom: 15px;">Current Stats</h3>
            <div style="background-color: #f0f9ff; border-left: 3px solid #0ea5e9; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <p style="margin: 0; color: #0c4a6e !important; font-weight: 600;">Available Spots</p>
                <p style="margin: 0; font-size: 24px; color: #0c4a6e !important; font-weight: 700;">28</p>
            </div>
            <div style="background-color: #fef2f2; border-left: 3px solid #ef4444; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <p style="margin: 0; color: #7f1d1d !important; font-weight: 600;">Occupied Spots</p>
                <p style="margin: 0; font-size: 24px; color: #7f1d1d !important; font-weight: 700;">12</p>
            </div>
            <div style="background-color: #fffbeb; border-left: 3px solid #f59e0b; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <p style="margin: 0; color: #78350f !important; font-weight: 600;">Under Maintenance</p>
                <p style="margin: 0; font-size: 24px; color: #78350f !important; font-weight: 700;">5</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def availability_page():
    st.markdown('<h1 class="section-header">The Parkmate Availability</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569; margin-bottom: 20px;">Check real-time parking space status</p>', unsafe_allow_html=True)
    
    # Filter options
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        section = st.selectbox("Section", ["All", "A", "B", "C"], key="filter_section")
    with col2:
        floor = st.selectbox("Floor", ["All", "1", "2", "3"], key="filter_floor")
    with col3:
        status = st.selectbox("Status", ["All", "Available", "Booked", "Maintenance"], key="filter_status")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get spots from database
    spots = get_all_spots()
    
    if not spots:
        st.markdown('<div class="important-info">No parking spots found.</div>', unsafe_allow_html=True)
        return
    
    # Apply filters
    filtered_spots = []
    for spot in spots:
        # Apply section filter
        if section != "All" and spot["section"] != section:
            continue
            
        # Apply floor filter
        if floor != "All" and spot["floor"] != int(floor):
            continue
            
        # Apply status filter
        if status != "All" and spot["status"].lower() != status.lower():
            continue
            
        filtered_spots.append(spot)
    
    # Display spots in a grid
    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    
    # Create rows with 5 spots each
    for i in range(0, len(filtered_spots), 5):
        row_spots = filtered_spots[i:i+5]
        cols = st.columns(5)
        
        for j, spot in enumerate(row_spots):
            with cols[j]:
                status_class = spot["status"].lower()
                spot_number = spot["spot_number"]
                section = spot["section"]
                floor = spot["floor"]
                
                st.markdown(f"""
                <div class="{status_class}">
                    <div style="font-size: 18px; margin-bottom: 5px;">{spot_number}</div>
                    <div>Section {section}, Floor {floor}</div>
                    <div style="font-size: 14px; margin-top: 5px; text-transform: uppercase;">{status_class}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display legend
    st.markdown("""
    <div style="margin-top: 30px; display: flex; justify-content: center; gap: 20px;">
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: #10B981; border-radius: 3px; margin-right: 5px;"></div>
            <span style="color: #333333;">Available</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: #EF4444; border-radius: 3px; margin-right: 5px;"></div>
            <span style="color: #333333;">Booked</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: #F59E0B; border-radius: 3px; margin-right: 5px;"></div>
            <span style="color: #333333;">Maintenance</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def booking_page():
    st.markdown('<h1 class="section-header">THE PARKMATE</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569; margin-bottom: 20px;">Reserve your parking spot</p>', unsafe_allow_html=True)
    
    # Get available spots from database
    available_spots = get_available_spots()
    
    if not available_spots:
        st.markdown('<div class="important-info">No available parking spots at the moment. Please check back later.</div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Convert spots to a format for the selectbox
    spot_options = [f"{spot['spot_number']} (Section {spot['section']}, Floor {spot['floor']})" for spot in available_spots]
    
    # Booking form
    selected_spot_index = st.selectbox("Select Parking Spot", range(len(spot_options)), format_func=lambda x: spot_options[x], key="select_spot")
    selected_spot = available_spots[selected_spot_index]
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date(), key="start_date")
        start_time = st.time_input("Start Time", datetime.now().time(), key="start_time")
    
    with col2:
        # Set end_date default to start_date, and end_time default to start_time + 2 hours
        default_end_time = (datetime.combine(datetime.now().date(), datetime.now().time()) + timedelta(hours=2)).time()
        end_date = st.date_input("End Date", start_date, key="end_date")
        end_time = st.time_input("End Time", default_end_time, key="end_time")
    
    # Calculate duration and cost
    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)
    
    if end_datetime <= start_datetime:
        st.markdown('<div class="important-info">End time must be after start time</div>', unsafe_allow_html=True)
        duration_hours = 0
        cost = 0
    else:
        duration = end_datetime - start_datetime
        duration_hours = duration.total_seconds() / 3600
        cost = duration_hours * 2  # $2 per hour
    
    # Display booking summary
    st.markdown(f"""
    <div style="margin-top: 20px; padding: 15px; background-color: #f8fafc; border-radius: 5px; border: 1px solid #cbd5e1;">
        <h3 style="color: #1E3A8A; margin-bottom: 10px;">Booking Summary</h3>
        <p style="color: #333333;"><strong>Parking Spot:</strong> {selected_spot['spot_number']} (Section {selected_spot['section']}, Floor {selected_spot['floor']})</p>
        <p style="color: #333333;"><strong>Duration:</strong> {duration_hours:.2f} hours</p>
        <p style="color: #333333;"><strong>Cost:</strong> ${cost:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Book spot button
    if st.button("Book Spot", key="book_spot"):
        if end_datetime <= start_datetime:
            st.markdown('<div class="important-info">Please select a valid time range</div>', unsafe_allow_html=True)
        else:
            # Format datetimes for database
            start_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            if book_spot(st.session_state.user['id'], selected_spot['id'], start_str, end_str):
                st.markdown('<div class="important-info" style="background-color: #d1fae5; border-left-color: #10b981; color: #065f46 !important;">Booking successful! Redirecting to My Bookings page...</div>', unsafe_allow_html=True)
                # Redirect to my bookings page after 2 seconds
                st.markdown("""
                <script>
                    setTimeout(function() {
                        window.location.href = '?page=my_bookings';
                    }, 2000);
                </script>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="important-info">Failed to book the spot. Please try again.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def my_bookings_page():
    st.markdown('<h1 class="section-header">My Parkmate Bookings</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569; margin-bottom: 20px;">Manage your parking reservations</p>', unsafe_allow_html=True)
    
    # Get user bookings from database
    bookings = get_user_bookings(st.session_state.user['id'])
    
    if not bookings:
        st.markdown('<div class="important-info">You have no bookings yet. Book a parking spot to get started!</div>', unsafe_allow_html=True)
        
        # Add a button to navigate to booking page
        if st.button("Book a Spot Now", key="no_bookings_button"):
            st.session_state.page = "book"
            st.experimental_rerun()
        return
    
    # Separate active and past bookings
    active_bookings = []
    past_bookings = []
    current_time = datetime.now()
    
    for booking in bookings:
        end_time = datetime.strptime(booking['end_time'], '%Y-%m-%d %H:%M:%S')
        if end_time > current_time and booking['status'] != 'cancelled':
            active_bookings.append(booking)
        else:
            past_bookings.append(booking)
    
    # Display active bookings
    if active_bookings:
        st.markdown('<h2 style="color: #1E3A8A; margin-top: 20px;">Active Bookings</h2>', unsafe_allow_html=True)
        
        for booking in active_bookings:
            # Create a card for each booking
            start_time = datetime.strptime(booking['start_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(booking['end_time'], '%Y-%m-%d %H:%M:%S')
            
            # Calculate duration and cost
            duration = end_time - start_time
            duration_hours = duration.total_seconds() / 3600
            cost = duration_hours * 2  # $2 per hour
            
            payment_color = "#10B981" if booking['payment_status'] == 'paid' else "#F59E0B"
            st.markdown(f'''
            <div class="booking-card">
                <div class="booking-title">Booking #{booking['id']} - {booking['spot_number']}</div>
                <div class="booking-info"><strong>Section:</strong> {booking['section']} | <strong>Floor:</strong> {booking['floor']}</div>
                <div class="booking-info"><strong>Start:</strong> {start_time.strftime('%Y-%m-%d %H:%M')}</div>
                <div class="booking-info"><strong>End:</strong> {end_time.strftime('%Y-%m-%d %H:%M')}</div>
                <div class="booking-info"><strong>Duration:</strong> {duration_hours:.2f} hours</div>
                <div class="booking-info"><strong>Cost:</strong> ${cost:.2f}</div>
                <div class="booking-info"><strong>Status:</strong> <span style="color: #10B981; font-weight: 600;">{booking['status'].title()}</span></div>
                <div class="booking-info"><strong>Payment:</strong> <span style="color: {payment_color}; font-weight: 600;">{booking['payment_status'].title()}</span></div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Cancel booking button
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"Cancel Booking", key=f"cancel_{booking['id']}"):
                    try:
                        if cancel_booking(booking['id'], booking['spot_id']):
                            st.markdown('<div class="important-info" style="background-color: #d1fae5; border-left-color: #10b981; color: #065f46 !important;">Booking cancelled successfully! Refreshing...</div>', unsafe_allow_html=True)
                            # Add JavaScript to refresh the page after 2 seconds
                            st.markdown("""
                            <script>
                                setTimeout(function() {
                                    window.location.reload();
                                }, 2000);
                            </script>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="important-info">Failed to cancel booking. Please try again.</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="important-info">Error cancelling booking: {e}</div>', unsafe_allow_html=True)
            
            with col2:
                if booking['payment_status'] == 'pending':
                    if st.button(f"Make Payment", key=f"pay_{booking['id']}"):
                        # This would normally connect to a payment processor
                        conn = None
                        try:
                            conn = get_db_connection()
                            if not conn:
                                st.markdown('<div class="important-info">Database connection error. Please try again.</div>', unsafe_allow_html=True)
                                return
                                
                            conn.execute("BEGIN TRANSACTION")
                            conn.execute("UPDATE bookings SET payment_status = 'paid' WHERE id = ?", (booking['id'],))
                            conn.commit()
                            st.markdown('<div class="important-info" style="background-color: #d1fae5; border-left-color: #10b981; color: #065f46 !important;">Payment successful! Refreshing...</div>', unsafe_allow_html=True)
                            # Add JavaScript to refresh the page after 2 seconds
                            st.markdown("""
                            <script>
                                setTimeout(function() {
                                    window.location.reload();
                                }, 2000);
                            </script>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="important-info">Payment error: {e}</div>', unsafe_allow_html=True)
                            if conn:
                                conn.rollback()
                        finally:
                            if conn:
                                conn.close()
    
    # Display past bookings
    if past_bookings:
        st.markdown('<h2 style="color: #1E3A8A; margin-top: 30px;">Booking History</h2>', unsafe_allow_html=True)
        
        # Create a table for past bookings
        st.markdown('<table class="styled-table">', unsafe_allow_html=True)
        st.markdown('''
        <tr>
            <th>Booking ID</th>
            <th>Spot</th>
            <th>Date</th>
            <th>Duration</th>
            <th>Cost</th>
            <th>Status</th>
        </tr>
        ''', unsafe_allow_html=True)
        
        for booking in past_bookings:
            start_time = datetime.strptime(booking['start_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(booking['end_time'], '%Y-%m-%d %H:%M:%S')
            
            # Calculate duration and cost
            duration = end_time - start_time
            duration_hours = duration.total_seconds() / 3600
            cost = duration_hours * 2  # $2 per hour
            
            status_color = "#EF4444" if booking['status'] == 'cancelled' else "#10B981"
            
            st.markdown(f'''
            <tr>
                <td>{booking['id']}</td>
                <td>{booking['spot_number']} (Section {booking['section']}, Floor {booking['floor']})</td>
                <td>{start_time.strftime('%Y-%m-%d')}</td>
                <td>{duration_hours:.2f} hours</td>
                <td>${cost:.2f}</td>
                <td style="color: {status_color}; font-weight: 600;">{booking['status'].title()}</td>
            </tr>
            ''', unsafe_allow_html=True)
        
        st.markdown('</table>', unsafe_allow_html=True)

# Add code for enhanced navigation and main application flow
def admin_page():
    st.markdown('<h1 class="section-header">The Parkmate Admin Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #475569; margin-bottom: 20px;">Manage your parking system</p>', unsafe_allow_html=True)
    
    # Admin functionality would go here
    st.markdown('<div class="important-info">Admin functionality is currently under development.</div>', unsafe_allow_html=True)

# Initialize session state for user management
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize page state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Main application flow
def main():
    # Check if user is logged in
    if not st.session_state.user:
        # Show login or register page based on query params
        # Show login or register page based on query params
        try:
            query_params = st.query_params
            page = query_params.get('page', ['login'])[0] if query_params.get('page') else 'login'
        except Exception as e:
            st.error(f"Error retrieving query parameters: {e}")
            page = 'login'
        if page == 'register':
            register_page()
        else:
            login_page()
    else:
        # User is logged in, show navigation and content
        with st.sidebar:
            st.markdown(f'<h2 style="color: #1E3A8A; text-align: center;">Welcome, {st.session_state.user["username"]}</h2>', unsafe_allow_html=True)
            
            # Improved navigation menu
            selected = option_menu(
                menu_title="Navigation",
                options=["Home", "Book Parking", "View Availability", "My Bookings"] + (["Admin Dashboard"] if st.session_state.user['is_admin'] else []),
                icons=["house", "p-square", "grid", "calendar-check"] + (["gear"] if st.session_state.user['is_admin'] else []),
                menu_icon="list",
                default_index=["home", "book", "availability", "my_bookings", "admin"].index(st.session_state.page) if st.session_state.page in ["home", "book", "availability", "my_bookings", "admin"] else 0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#f1f5f9", "border-radius": "10px"},
                    "icon": {"color": "#1E3A8A", "font-size": "14px"},
                    "nav-link": {"color": "#475569", "font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#e2e8f0"},
                    "nav-link-selected": {"background-color": "#1E3A8A", "color": "white", "font-weight": "600"}
                }
            )
            
            # Update page state based on navigation selection
            if selected == "Home":
                st.session_state.page = "home"
            elif selected == "Book Parking":
                st.session_state.page = "book"
            elif selected == "View Availability":
                st.session_state.page = "availability"
            elif selected == "My Bookings":
                st.session_state.page = "my_bookings"
            elif selected == "Admin Dashboard":
                st.session_state.page = "admin"
            
            # Logout button
            if st.button("Logout", key="logout"):
                st.session_state.user = None
                st.session_state.page = "home"
                st.experimental_rerun()
        
        # Display content based on selected page
        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "book":
            booking_page()
        elif st.session_state.page == "availability":
            availability_page()
        elif st.session_state.page == "my_bookings":
            my_bookings_page()
        elif st.session_state.page == "admin" and st.session_state.user['is_admin']:
            admin_page()
        else:
            home_page()

# Run the main application
if __name__ == "__main__":
    main()
