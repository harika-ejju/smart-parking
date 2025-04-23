import streamlit as st
from datetime import datetime, timedelta
import json
import sys
import os
import re

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import save_booking, get_parking_space, update_parking_space_status
from utils import format_time, calculate_price, validate_email, validate_phone, validate_license_plate

def booking_form(space_id=None):
    """
    Creates a booking form for users to reserve a parking space

    Args:
        space_id (int, optional): ID of the selected parking space

    Returns:
        dict: Form data if submitted successfully, None otherwise
    """
    if space_id is None and 'selected_space' in st.session_state:
        space_id = st.session_state.selected_space

    if space_id is None:
        st.warning("Please select a parking space from the grid first")
        return None

    # Get space details
    try:
        space = get_parking_space(space_id)
        if not space:  # Handle case where space is not found
            st.error(f"Parking space {space_id} not found.")
            # Use dummy data as fallback or return
            space = {
                "id": space_id,
                "status": "unavailable",  # Mark as unavailable if not found
                "price_per_hour": 2.5,
                "location": f"Zone {(space_id // 10) + 1}",
                "size": "Standard"
            }
            # Optionally return None here if space must exist
            # return None
    except Exception as e:  # Catch specific exceptions if possible
        st.error(f"Error fetching parking space details: {e}")
        # Dummy data if database not set up or error occurs
        space = {
            "id": space_id,
            "status": "unavailable",
            "price_per_hour": 2.5,
            "location": f"Zone {(space_id // 10) + 1}",
            "size": "Standard"
        }