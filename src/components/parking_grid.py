import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_all_parking_spaces, update_parking_space_status
from utils import format_time, get_status_color, calculate_price

def create_parking_grid(num_rows=5, num_cols=6):
    """
    Creates a grid visualization of parking spaces
    
    Args:
        num_rows (int): Number of rows in the parking grid
        num_cols (int): Number of columns in the parking grid
        
    Returns:
        None: Displays the grid in the Streamlit app
    """
    st.markdown("""
    <style>
        .parking-spot {
            width: 100%;
            height: 100px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            margin: 0.25rem;
            cursor: pointer;
            text-align: center;
            font-weight: bold;
        }
        .available {
            background-color: #10B981;
            color: white;
        }
        .occupied {
            background-color: #EF4444;
            color: white;
        }
        .reserved {
            background-color: #F59E0B;
            color: white;
        }
        .selected {
            border: 3px solid #3B82F6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## Parking Space Availability")
    st.markdown("### Click on an available space to select it for booking")
    
    # Fetch parking spaces from the database
    try:
        parking_spaces = get_all_parking_spaces()
    except:
        # If database not set up yet, use dummy data
        parking_spaces = [
            {"id": i, "status": np.random.choice(["available", "occupied", "reserved"], p=[0.6, 0.3, 0.1]), 
             "price_per_hour": 2.0 + (i % 3), "location": f"Zone {(i // 10) + 1}", "size": "Standard"} 
            for i in range(num_rows * num_cols)
        ]
    
    # Create the grid
    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            index = row * num_cols + col
            if index < len(parking_spaces):
                space = parking_spaces[index]
                status = space.get("status", "available")
                space_id = space.get("id", index)
                
                # Determine the color based on status
                color_class = "available" if status == "available" else "occupied" if status == "occupied" else "reserved"
                
                # Create the parking spot
                with cols[col]:
                    spot_html = f"""
                    <div id="spot-{space_id}" class="parking-spot {color_class}" 
                         onclick="handleSpotClick({space_id}, '{status}')">
                        <div>
                            <div>Spot {space_id}</div>
                            <div>{space.get('location', 'Zone A')}</div>
                            <div>${space.get('price_per_hour', 2.00)}/hr</div>
                        </div>
                    </div>
                    """
                    st.markdown(spot_html, unsafe_allow_html=True)
                    
                    # Add JavaScript for interactivity
                    if status == "available":
                        if st.button(f"Book #{space_id}", key=f"book_{space_id}"):
                            st.session_state.selected_space = space_id
                            st.session_state.selected_space_details = space
                            st.rerun()

    # JavaScript to handle spot selection
    st.markdown("""
    <script>
        function handleSpotClick(spotId, status) {
            if (status === "available") {
                // Communicate with Streamlit
                const selection = {
                    spot_id: spotId,
                    selected: true
                };
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: selection
                }, "*");
                
                // Visual feedback
                document.querySelectorAll(".parking-spot").forEach(spot => {
                    spot.classList.remove("selected");
                });
                document.getElementById(`spot-${spotId}`).classList.add("selected");
            }
        }
    </script>
    """, unsafe_allow_html=True)
    
    return

def update_grid_status():
    """
    Updates the status of the parking grid in real-time
    
    Returns:
        None: Updates the display in the Streamlit app
    """
    # In a real application, this would fetch data from a database or API
    # For demo purposes, we'll simulate status changes every few seconds
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
        
    current_time = datetime.now()
    if current_time - st.session_state.last_update > timedelta(seconds=30):
        # Update some random spots
        try:
            spaces = get_all_parking_spaces()
            for space in np.random.choice(spaces, size=min(3, len(spaces)), replace=False):
                new_status = np.random.choice(["available", "occupied", "reserved"], p=[0.5, 0.3, 0.2])
                update_parking_space_status(space['id'], new_status)
        except:
            pass
        
        st.session_state.last_update = current_time
        
    return

def display_parking_details(space_id):
    """
    Displays detailed information about a selected parking space
    
    Args:
        space_id (int): ID of the selected parking space
        
    Returns:
        None: Displays the details in the Streamlit app
    """
    if not space_id:
        return
    
    try:
        # Get space details from database
        spaces = get_all_parking_spaces()
        space = next((s for s in spaces if s['id'] == space_id), None)
    except:
        # Dummy data if database not set up
        space = {
            "id": space_id,
            "status": "available",
            "price_per_hour": 2.5,
            "location": f"Zone {(space_id // 10) + 1}",
            "size": "Standard",
            "features": ["Security Camera", "Covered"]
        }
    
    if space:
        st.markdown(f"""
        <div class="p-4 bg-white rounded-lg shadow-md">
            <h3 class="text-xl font-bold">Parking Space #{space_id}</h3>
            <p><strong>Location:</strong> {space.get('location', 'Unknown')}</p>
            <p><strong>Status:</strong> {space.get('status', 'Unknown')}</p>
            <p><strong>Price:</strong> ${space.get('price_per_hour', 0.0)}/hour</p>
            <p><strong>Size:</strong> {space.get('size', 'Standard')}</p>
            <p><strong>Features:</strong> {', '.join(space.get('features', ['None']))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return

def filter_parking_spaces(location=None, status=None, price_range=None, features=None):
    """
    Filters the parking spaces based on criteria
    
    Args:
        location (str, optional): Filter by location
        status (str, optional): Filter by status
        price_range (tuple, optional): Filter by price range (min, max)
        features (list, optional): Filter by features
        
    Returns:
        list: Filtered parking spaces
    """
    st.markdown("### Filter Parking Spaces")
    
    with st.form(key="filter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            location_filter = st.selectbox("Location", ["All", "Zone 1", "Zone 2", "Zone 3"], index=0)
            status_filter = st.selectbox("Status", ["All", "Available", "Occupied", "Reserved"], index=0)
        
        with col2:
            price_range = st.slider("Price Range ($ per hour)", 1.0, 10.0, (1.0, 10.0), step=0.5)
            features_filter = st.multiselect("Features", ["Security Camera", "Covered", "Near Entrance", "EV Charging", "Handicap Accessible"])
        
        submit_button = st.form_submit_button(label="Apply Filters")
    
    # Return the filters if the form is submitted
    if submit_button:
        return {
            "location": None if location_filter == "All" else location_filter,
            "status": None if status_filter == "All" else status_filter.lower(),
            "price_range": price_range,
            "features": features_filter
        }
    
    return None

