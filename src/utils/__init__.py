"""
Utility functions for the Smart Parking application.
This module contains helper functions for time formatting, validation, price calculation,
parking space status management, and other general utilities.
"""

import re
import uuid
import datetime
from typing import Dict, List, Optional, Union, Tuple
import pytz

# ------------------------------
# Time formatting and conversion
# ------------------------------

def get_current_time() -> datetime.datetime:
    """
    Returns the current datetime with timezone information.
    """
    return datetime.datetime.now(pytz.UTC)

def format_datetime(dt: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string representation.
    
    Args:
        dt: The datetime to format
        format_str: The format string to use
        
    Returns:
        Formatted datetime string
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
    """
    Parse a string into a datetime object.
    
    Args:
        date_str: The string to parse
        format_str: The format string to use
        
    Returns:
        Parsed datetime object with UTC timezone
    """
    dt = datetime.datetime.strptime(date_str, format_str)
    return pytz.UTC.localize(dt) if dt.tzinfo is None else dt

def calculate_duration(start_time: datetime.datetime, end_time: datetime.datetime) -> datetime.timedelta:
    """
    Calculate the duration between two datetime objects.
    
    Args:
        start_time: The start datetime
        end_time: The end datetime
        
    Returns:
        A timedelta object representing the duration
    """
    # Ensure both times have timezone info for proper comparison
    if start_time.tzinfo is None:
        start_time = pytz.UTC.localize(start_time)
    if end_time.tzinfo is None:
        end_time = pytz.UTC.localize(end_time)
        
    return end_time - start_time

def format_duration(duration: datetime.timedelta) -> str:
    """
    Format a timedelta object to a human-readable string.
    
    Args:
        duration: The duration to format
        
    Returns:
        A formatted string like "2 hours 30 minutes"
    """
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 and not hours and not minutes:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
    return " ".join(parts) if parts else "0 seconds"


# ---------------------
# Input validation
# ---------------------

def is_valid_license_plate(license_plate: str) -> bool:
    """
    Validate if a license plate has the correct format.
    
    Args:
        license_plate: The license plate to validate
        
    Returns:
        True if valid, False otherwise
    """
    # This is a simple example - adjust regex based on your country's license plate format
    pattern = r'^[A-Z0-9]{1,8}$'
    return bool(re.match(pattern, license_plate.upper()))

def is_valid_email(email: str) -> bool:
    """
    Validate if an email has the correct format.
    
    Args:
        email: The email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    """
    Validate if a phone number has the correct format.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove spaces, dashes, and parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^(\+\d{1,3})?\d{10,15}$'
    return bool(re.match(pattern, cleaned_phone))

def validate_booking_time(start_time: datetime.datetime, end_time: datetime.datetime) -> Tuple[bool, str]:
    """
    Validate if booking times are valid.
    
    Args:
        start_time: The booking start time
        end_time: The booking end time
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    now = get_current_time()
    
    if start_time < now:
        return False, "Start time must be in the future"
    
    if end_time <= start_time:
        return False, "End time must be after start time"
    
    max_duration = datetime.timedelta(days=7)  # Maximum booking duration
    if end_time - start_time > max_duration:
        return False, f"Booking duration cannot exceed {max_duration.days} days"
    
    return True, ""


# ------------------------
# Price calculation helpers
# ------------------------

def calculate_parking_fee(
    vehicle_type: str,
    duration: datetime.timedelta,
    is_premium: bool = False
) -> float:
    """
    Calculate parking fee based on vehicle type and duration.
    
    Args:
        vehicle_type: Type of vehicle (car, motorcycle, truck, etc.)
        duration: Parking duration
        is_premium: Whether premium parking space is used
        
    Returns:
        The calculated fee
    """
    # Base hourly rates
    hourly_rates = {
        "motorcycle": 2.0,
        "car": 5.0,
        "suv": 7.0,
        "truck": 10.0
    }
    
    # Get base rate or default to car rate if type not found
    base_hourly_rate = hourly_rates.get(vehicle_type.lower(), hourly_rates["car"])
    
    # Premium spaces cost extra
    if is_premium:
        base_hourly_rate *= 1.5
    
    # Calculate hours, rounded up
    hours = duration.total_seconds() / 3600
    charged_hours = math.ceil(hours)
    
    # Apply discounts for longer durations
    if charged_hours > 12:
        # 10% discount for more than 12 hours
        return charged_hours * base_hourly_rate * 0.9
    if charged_hours > 24:
        # 20% discount for more than 24 hours
        return charged_hours * base_hourly_rate * 0.8
    
    return charged_hours * base_hourly_rate

def apply_discount(amount: float, discount_code: str) -> Tuple[float, float]:
    """
    Apply discount to parking fee based on discount code.
    
    Args:
        amount: The original amount
        discount_code: The discount code to apply
        
    Returns:
        Tuple of (discounted_amount, discount_amount)
    """
    # Example discount codes
    discounts = {
        "NEWUSER": 0.20,  # 20% off
        "WEEKEND": 0.15,  # 15% off
        "LOYALTY": 0.10,  # 10% off
    }
    
    discount_percentage = discounts.get(discount_code.upper(), 0)
    discount_amount = amount * discount_percentage
    discounted_amount = amount - discount_amount
    
    return discounted_amount, discount_amount


# -----------------------------
# Parking space status utilities
# -----------------------------

def get_status_color(status: str) -> str:
    """
    Get color code for parking space status.
    
    Args:
        status: The status string
        
    Returns:
        CSS color class name
    """
    status_map = {
        "available": "bg-green-500",
        "occupied": "bg-red-500",
        "reserved": "bg-yellow-500",
        "maintenance": "bg-gray-500",
        "disabled": "bg-gray-300",
    }
    return status_map.get(status.lower(), "bg-blue-500")

def is_space_available(status: str) -> bool:
    """
    Check if a parking space is available for booking.
    
    Args:
        status: The status of the space
        
    Returns:
        True if available, False otherwise
    """
    return status.lower() == "available"

def update_space_status(current_status: str, action: str) -> str:
    """
    Determine new status based on current status and action taken.
    
    Args:
        current_status: Current status of the parking space
        action: Action being performed (book, check_in, check_out, maintenance)
        
    Returns:
        New status string
    """
    status_transitions = {
        "available": {
            "book": "reserved",
            "check_in": "occupied",
            "maintenance": "maintenance"
        },
        "reserved": {
            "check_in": "occupied",
            "cancel": "available",
            "maintenance": "maintenance"
        },
        "occupied": {
            "check_out": "available",
            "maintenance": "maintenance"
        },
        "maintenance": {
            "complete": "available"
        }
    }
    
    return status_transitions.get(current_status.lower(), {}).get(action.lower(), current_status)


# ---------------------
# General helper functions
# ---------------------

def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique ID string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}-{unique_id}" if prefix else unique_id

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format a currency amount.
    
    Args:
        amount: The amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
    }
    
    symbol = currency_symbols.get(currency, currency + " ")
    
    # Format with 2 decimal places
    if currency == "JPY":
        # JPY typically doesn't use decimal places
        return f"{symbol}{round(amount):,}"
    return f"{symbol}{amount:.2f}"

def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated string with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

