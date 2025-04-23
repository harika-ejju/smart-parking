import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Smart Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'user' not in st.session_state:
    st.session_state.user = None
if 'admin' not in st.session_state:
    st.session_state.admin = False
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'parking_data' not in st.session_state:
    # Mock data for parking spaces
    st.session_state.parking_data = {
        'A1': {'status': 'available', 'type': 'standard'},
        'A2': {'status': 'occupied', 'type': 'standard'},
        'A3': {'status': 'available', 'type': 'standard'},
        'B1': {'status': 'available', 'type': 'disabled'},
        'B2': {'status': 'available', 'type': 'premium'},
        'B3': {'status': 'occupied', 'type': 'premium'},
    }
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

# Tailwind CSS integration
def load_tailwind():
    return """
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .stApp {
            background-color: #f0f2f5;
        }
        .card {
            @apply bg-white rounded-lg shadow-md p-6 mb-4;
            color: #333333;
        }
        .btn-primary {
            @apply bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded;
        }
        .btn-secondary {
            @apply bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded;
        }
        .header {
            @apply text-2xl font-bold text-gray-900 mb-4;
        }
        .subheader {
            @apply text-xl font-semibold text-gray-800 mb-3;
        }
        p, li {
            color: #333333;
            font-size: 1rem;
        }
    </style>
    """

# Inject Tailwind CSS
st.markdown(load_tailwind(), unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        margin-bottom: 1rem !important;
    }
    .section-header {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #1e40af !important;
        margin-bottom: 0.5rem !important;
    }
    .parking-space {
        display: inline-block;
        width: 100px;
        height: 60px;
        margin: 5px;
        text-align: center;
        line-height: 60px;
        border-radius: 5px;
        font-weight: bold;
    }
    .available {
        background-color: #10b981;
        color: #ffffff;
    }
    .occupied {
        background-color: #ef4444;
        color: #ffffff;
    }
    .disabled {
        background-color: #6b7280;
        color: #ffffff;
    }
    .premium {
        border: 3px solid #f59e0b;
        background-color: #10b981;
    }
    .card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .card h2 {
        color: #1e40af;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .card p, .card li {
        color: #333333;
        font-size: 1rem;
        line-height: 1.5;
    }
    button {
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: none;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    button:hover {
        background-color: #1d4ed8;
    }
    .stButton button {
        width: 100%;
        margin-bottom: 10px;
    }
    /* Improving readability of sidebar text */
    .css-1d391kg, .css-163ttbj, .css-10trblm {
        color: #111827 !important;
    }
    /* Making labels more visible */
    label.css-qrbaxs {
        color: #111827 !important;
        font-weight: 500 !important;
    }
    /* Input fields styling */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] div {
        background-color: #ffffff !important;
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
def navigation():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/parking.png", width=100)
        st.markdown("<h1 class='main-header'>Smart Parking</h1>", unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Book Parking", "View Availability", "My Bookings", "Admin"],
            icons=["house", "calendar-plus", "eye", "list-check", "shield-lock"],
            menu_icon="list",
            default_index=0,
        )
        
        st.session_state.page = selected
        
        # Mock Login section in sidebar
        if st.session_state.user is None:
            st.sidebar.subheader("Login")
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if username and password:
                    st.session_state.user = username
                    if username == "admin" and password == "admin":
                        st.session_state.admin = True
                    st.experimental_rerun()
        else:
            st.sidebar.success(f"Logged in as {st.session_state.user}")
            if st.sidebar.button("Logout"):
                st.session_state.user = None
                st.session_state.admin = False
                st.experimental_rerun()

    return selected

# Home page
def home_page():
    st.markdown("<h1 class='main-header'>Welcome to Smart Parking System</h1>", unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2 class="subheader">Efficient Parking Management</h2>
            <p style="color: #333333; margin-bottom: 10px;">Our smart parking system uses artificial intelligence to optimize parking space utilization, 
            reduce congestion, and minimize carbon emissions.</p>
            <ul style="color: #333333; margin-left: 20px;">
                <li style="margin-bottom: 5px;">Real-time parking availability tracking</li>
                <li style="margin-bottom: 5px;">Seamless booking experience</li>
                <li style="margin-bottom: 5px;">Secure payment options</li>
                <li style="margin-bottom: 5px;">Vehicle protection features</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h2 class="subheader">How It Works</h2>
            <ol style="color: #333333; margin-left: 20px;">
                <li style="margin-bottom: 5px;">Check parking availability in real-time</li>
                <li style="margin-bottom: 5px;">Book your preferred parking spot</li>
                <li style="margin-bottom: 5px;">Receive confirmation and directions</li>
                <li style="margin-bottom: 5px;">Park your vehicle securely</li>
                <li style="margin-bottom: 5px;">Pay seamlessly through our app</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h2 class="subheader">Current Status</h2>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Total Spaces:</strong> 24</p>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Available:</strong> <span style="color: #10b981; font-weight: bold;">18</span></p>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Occupied:</strong> <span style="color: #ef4444; font-weight: bold;">6</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h2 class="subheader">Quick Actions</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Book a Spot Now"):
            st.session_state.page = "Book Parking"
            st.experimental_rerun()
        if st.button("View Current Availability"):
            st.session_state.page = "View Availability"
            st.experimental_rerun()

# Book Parking page
def book_parking_page():
    st.markdown("<h1 class='main-header'>Book a Parking Spot</h1>", unsafe_allow_html=True)
    
    if st.session_state.user is None:
        st.warning("Please login to book a parking spot")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h2 class='section-header'>Booking Details</h2>", unsafe_allow_html=True)
        date = st.date_input("Select Date", min_value=datetime.today())
        time_in = st.time_input("Entry Time", value=datetime.now().replace(minute=0, second=0, microsecond=0))
        duration = st.selectbox("Duration", options=[1, 2, 3, 4, 5, 6, 12, 24], index=0, format_func=lambda x: f"{x} hour(s)")
        vehicle_type = st.selectbox("Vehicle Type", options=["Car", "Motorcycle", "Van", "Truck"])
        license_plate = st.text_input("License Plate Number")
        
    with col2:
        st.markdown("<h2 class='section-header'>Select Parking Type</h2>", unsafe_allow_html=True)
        parking_type = st.radio("Parking Type", options=["Standard", "Premium", "Disabled"])
        
        st.markdown("<h2 class='section-header'>Payment Method</h2>", unsafe_allow_html=True)
        payment_method = st.selectbox("Payment Method", options=["Credit Card", "Debit Card", "Mobile Payment", "Cash"])
        
        total_cost = duration * (10 if parking_type == "Standard" else 15 if parking_type == "Premium" else 8)
        st.markdown(f"<h3>Total Cost: ${total_cost}</h3>", unsafe_allow_html=True)
    
    if st.button("Book Now"):
        if not license_plate:
            st.error("Please enter your license plate number")
        else:
            # Here we would normally process the booking and save to a database
            # For now, just add to session state
            booking = {
                "id": len(st.session_state.bookings) + 1,
                "user": st.session_state.user,
                "date": date.strftime("%Y-%m-%d"),
                "time_in": time_in.strftime("%H:%M"),
                "duration": duration,
                "vehicle_type": vehicle_type,
                "license_plate": license_plate,
                "parking_type": parking_type,
                "payment_method": payment_method,
                "total_cost": total_cost,
                "status": "Confirmed"
            }
            st.session_state.bookings.append(booking)
            st.success("Booking confirmed! You can view your booking details in the My Bookings section.")

# View Availability page
def view_availability_page():
    st.markdown("<h1 class='main-header'>Parking Availability</h1>", unsafe_allow_html=True)
    
    date = st.date_input("Select Date", min_value=datetime.today())
    time_slot = st.selectbox("Select Time Slot", options=[f"{i:02d}:00" for i in range(24)])
    
    st.markdown("<h2 class='section-header'>Current Availability</h2>", unsafe_allow_html=True)
    
    # Display parking lot visualization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Mock visualization of parking spaces
        st.markdown("<div style='background-color: #e5e7eb; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        for row in ["A", "B", "C"]:
            for i in range(1, 5):
                space_id = f"{row}{i}"
                status = "available"
                space_type = "standard"
                
                if space_id in st.session_state.parking_data:
                    status = st.session_state.parking_data[space_id]['status']
                    space_type = st.session_state.parking_data[space_id]['type']
                
                st.markdown(f"""
                <div class="parking-space {status} {space_type}">
                    {space_id}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);'>
            <h3 style="color: #1e40af; font-weight: 600; margin-bottom: 10px;">Legend</h3>
            <div class="parking-space available">Available</div>
            <div class="parking-space occupied">Occupied</div>
            <div class="parking-space available premium">Premium</div>
            <div class="parking-space available disabled">Disabled</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);'>
            <h3 style="color: #1e40af; font-weight: 600; margin-bottom: 10px;">Statistics</h3>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Total Spaces:</strong> 24</p>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Available:</strong> <span style="color: #10b981; font-weight: bold;">18</span></p>
            <p style="color: #333333; margin-bottom: 5px;"><strong>Occupied:</strong> <span style="color: #ef4444; font-weight: bold;">6</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.user is not None:
        if st.button("Book Selected Space"):
            st.session_state.page = "Book Parking"
            st.experimental_rerun()

# My Bookings page
def my_bookings_page():
    st.markdown("<h1 class='main-header'>My Bookings</h1>", unsafe_allow_html=True)
    
    if st.session_state.user is None:
        st.warning("Please login to view your bookings")
        return
    
    user_bookings = [b for b in st.session_state.bookings if b["user"] == st.session_state.user]
    
    if not user_bookings:
        st.info("You don't have any bookings yet. Book a parking spot to see your bookings here.")
    else:
        # Filter options
        col1, col2 = st.columns([1, 1])
        with col1:
            filter_status = st.selectbox("Filter by Status", options=["All", "Confirmed", "Cancelled", "Completed"])
        with col2:
            sort_by = st.selectbox("Sort by", options=["Date (Newest)", "Date (Oldest)", "Duration", "Cost"])
        
        for booking in user_bookings:
            with st.expander(f"Booking #{booking['id']} - {booking['date']} - {booking['status']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Date:** {booking['date']}")
                    st.markdown(f"**Time:** {booking['time_in']} for {booking['duration']} hour(s)")
                    st.markdown(f"**Vehicle:** {booking['vehicle_type']} ({booking['license_plate']})")
                    st.markdown(f"**Parking Type:** {booking['parking_type']}")
                
                with col2:
                    st.markdown(f"**Total Cost:** ${booking['total_cost']}")
                    st.markdown(f"**Payment Method:** {booking['payment_method']}")
                    st.markdown(f"**Status:** {booking['status']}")
                    
                    if booking['status'] == "Confirmed":
                        if st.button(f"Cancel Booking #{booking['id']}", key=f"cancel_{booking['id']}"):
                            try:
                                # Find the booking in the session state and update its status
                                for i, b in enumerate(st.session_state.bookings):
                                    if b['id'] == booking['id']:
                                        st.session_state.bookings[i]['status'] = "Cancelled"
                                        st.success(f"Booking #{booking['id']} has been cancelled successfully.", icon="✅")
                                        st.experimental_rerun()
                                        break
                            except Exception as e:
                                st.error(f"Error cancelling booking: {str(e)}", icon="❌")
                    elif booking['status'] == "Cancelled":
                        st.info("This booking has been cancelled.")
                    elif booking['status'] == "Completed":
                        st.success("This booking has been completed successfully.")

# Admin page
def admin_page():
    st.markdown("<h1 class='main-header'>Admin Dashboard</h1>", unsafe_allow_html=True)
    
    if not st.session_state.admin:
        st.error("Access denied. You need admin privileges to view this page.", icon="🔒")
        return
    
    st.markdown("<h2 class='section-header'>System Overview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Bookings", len(st.session_state.bookings))
    with col2:
        active_bookings = len([b for b in st.session_state.bookings if b['status'] == "Confirmed"])
        st.metric("Active Bookings", active_bookings)
    with col3:
        st.metric("Available Spaces", 18)  # In a real system, this would be calculated
    
    # All bookings
    st.markdown("<h2 class='section-header'>All Bookings</h2>", unsafe_allow_html=True)
    if not st.session_state.bookings:
        st.info("No bookings available in the system.")
    else:
        df = pd.DataFrame(st.session_state.bookings)
        st.dataframe(df)

    # Database management
    st.markdown("<h2 class='section-header'>Database Management</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Initialize Database"):
            try:
                # This is where the database initialization would go
                # For this mock app, we'll just reset our session state data
                
                # Initialize parking spaces
                parking_data = {}
                for row in ["A", "B", "C", "D", "E"]:
                    for i in range(1, 10):
                        space_id = f"{row}{i}"
                        # Randomly set some spaces as occupied for demo
                        status = "available" if np.random.rand() > 0.3 else "occupied"
                        # Randomly assign space types
                        type_rand = np.random.rand()
                        if type_rand < 0.7:
                            space_type = "standard"
                        elif type_rand < 0.9:
                            space_type = "premium"
                        else:
                            space_type = "disabled"
                        
                        parking_data[space_id] = {"status": status, "type": space_type}
                
                st.session_state.parking_data = parking_data
                
                # Initialize users (in a real app, this would go to a database)
                # We're not storing this in session for simplicity
                
                # Initialize sample bookings
                sample_bookings = []
                users = ["john_doe", "jane_smith", "admin"]
                statuses = ["Confirmed", "Cancelled", "Completed"]
                
                for i in range(1, 11):
                    booking_date = (datetime.today() - timedelta(days=np.random.randint(0, 10))).strftime("%Y-%m-%d")
                    booking_time = f"{np.random.randint(8, 20):02d}:00"
                    duration = np.random.choice([1, 2, 3, 4, 6, 12])
                    vehicle_type = np.random.choice(["Car", "Motorcycle", "Van", "Truck"])
                    license_plate = f"ABC{np.random.randint(1000, 9999)}"
                    parking_type = np.random.choice(["Standard", "Premium", "Disabled"])
                    payment_method = np.random.choice(["Credit Card", "Debit Card", "Mobile Payment", "Cash"])
                    total_cost = duration * (10 if parking_type == "Standard" else 15 if parking_type == "Premium" else 8)
                    status = np.random.choice(statuses, p=[0.5, 0.2, 0.3])
                    
                    booking = {
                        "id": i,
                        "user": np.random.choice(users),
                        "date": booking_date,
                        "time_in": booking_time,
                        "duration": duration,
                        "vehicle_type": vehicle_type,
                        "license_plate": license_plate,
                        "parking_type": parking_type,
                        "payment_method": payment_method,
                        "total_cost": total_cost,
                        "status": status
                    }
                    sample_bookings.append(booking)
                
                # Add completed bookings with proper error handling
                try:
                    for i in range(11, 16):
                        # Create completed bookings from 5-15 days ago
                        days_ago = np.random.randint(5, 16)
                        booking_date = (datetime.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                        booking_time = f"{np.random.randint(8, 20):02d}:00"
                        duration = np.random.choice([1, 2, 3, 4])
                        vehicle_type = np.random.choice(["Car", "Motorcycle"])
                        license_plate = f"XYZ{np.random.randint(1000, 9999)}"
                        parking_type = np.random.choice(["Standard", "Premium"])
                        payment_method = np.random.choice(["Credit Card", "Mobile Payment"])
                        total_cost = duration * (10 if parking_type == "Standard" else 15)
                        
                        completed_booking = {
                            "id": i,
                            "user": np.random.choice(users),
                            "date": booking_date,
                            "time_in": booking_time,
                            "duration": duration,
                            "vehicle_type": vehicle_type,
                            "license_plate": license_plate,
                            "parking_type": parking_type,
                            "payment_method": payment_method,
                            "total_cost": total_cost,
                            "status": "Completed"
                        }
                        sample_bookings.append(completed_booking)
                except Exception as e:
                    st.error(f"Error creating completed bookings: {str(e)}", icon="❌")
                    
                st.session_state.bookings = sample_bookings
                
                st.success("Database initialized successfully with sample data!", icon="✅")
            except Exception as e:
                st.error(f"Error initializing database: {str(e)}", icon="❌")
    
    with col2:
        if st.button("Clean Database"):
            try:
                # In a real app, this would perform database cleanup
                # For our mock app, let's remove old completed and cancelled bookings
                
                # Remove bookings older than 30 days
                thirty_days_ago = datetime.today() - timedelta(days=30)
                
                new_bookings = []
                cleaned_count = 0
                
                for booking in st.session_state.bookings:
                    # Parse the date
                    booking_date = datetime.strptime(booking['date'], "%Y-%m-%d")
                    
                    # Keep booking if it's newer than 30 days or it's still confirmed
                    if (booking_date >= thirty_days_ago) or (booking['status'] == "Confirmed"):
                        new_bookings.append(booking)
                    else:
                        cleaned_count += 1
                
                st.session_state.bookings = new_bookings
                
                st.success(f"Database cleaned successfully! Removed {cleaned_count} old bookings.", icon="✅")
            except Exception as e:
                st.error(f"Error cleaning database: {str(e)}", icon="❌")

# Main app logic
def main():
    try:
        selected = navigation()
        
        if selected == "Home":
            home_page()
        elif selected == "Book Parking":
            book_parking_page()
        elif selected == "View Availability":
            view_availability_page()
        elif selected == "My Bookings":
            my_bookings_page()
        elif selected == "Admin":
            admin_page()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}", icon="❌")
        st.markdown("""
        <div style="background-color: #FFEBEE; padding: 15px; border-radius: 5px; border-left: 5px solid #D32F2F; margin-bottom: 15px;">
            <h3 style="color: #B71C1C; margin-top: 0;">Error Details</h3>
            <p style="color: #333333; font-size: 16px;">The application encountered an unexpected error. Please try refreshing the page or contact support if the issue persists.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
