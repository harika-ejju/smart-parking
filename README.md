# Smart Parking Management System

## Project Description
The Smart Parking Management System is an artificial intelligence-based solution designed to address the challenges of inefficient parking space utilization. The system helps reduce time wastage, traffic congestion, CO2 emissions, and provides flexible payment methods while enhancing security for parked vehicles.

This application provides real-time parking management capabilities by dynamically allocating parking slots based on current availability, allowing users to book specific slots through an intuitive AI-powered interface, and ensuring vehicles are parked in their designated locations.

## Features

- **Real-time Parking Space Monitoring**: View availability of parking spaces in real-time
- **Dynamic Parking Slot Allocation**: System intelligently assigns optimal parking spaces
- **Parking Reservation System**: Book parking slots in advance through the application
- **Vehicle Verification**: Ensures cars are parked in their correct designated spaces
- **Flexible Payment Options**: Multiple payment methods for user convenience
- **Administrative Dashboard**: Monitoring and management tools for parking operators
- **User Account Management**: Registration, history tracking, and preference settings
- **Interactive Parking Map**: Visual representation of the parking facility
- **Notifications**: Alerts for booking confirmations, reminders, and updates
- **Analytics and Reporting**: Usage statistics and trend analysis

## Installation Instructions

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd smart_parking
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the project root
   - Add necessary environment variables (database connections, API keys, etc.)

## Usage Guide

1. **Start the application**
   ```
   cd src
   streamlit run app.py
   ```

2. **Navigate the application**
   - **Home**: View dashboard and system overview
   - **Book Parking**: Reserve a parking slot for a specific time period
   - **View Availability**: Check real-time parking space availability
   - **My Bookings**: Manage your current and past bookings
   - **Admin Panel**: Access administrative features (for authorized users)

3. **Booking a Parking Space**
   - Select the date and time for your parking
   - Choose a parking slot from the available options
   - Complete payment
   - Receive confirmation and parking details

4. **Managing Bookings**
   - View active bookings
   - Modify or cancel existing bookings (subject to cancellation policy)
   - View booking history

## Project Structure

```
smart_parking/
├── requirements.txt       # Project dependencies
├── README.md             # Project documentation
├── src/                  # Source code
│   ├── __init__.py
│   ├── app.py            # Main Streamlit application
│   ├── database.py       # Database connections and operations
│   ├── models/           # Data models
│   │   └── __init__.py
│   ├── utils/            # Utility functions
│   │   └── __init__.py
│   └── components/       # UI components
│       ├── __init__.py
│       ├── parking_grid.py    # Parking visualization
│       └── booking_form.py    # Booking interface
├── static/              # Static assets
│   ├── css/             # CSS styles
│   └── images/          # Image assets
└── tests/               # Test suite
    └── __init__.py
```

## Technologies Used

- **Streamlit**: Web application framework for the user interface
- **Tailwind CSS**: Styling and responsive design
- **SQLite/SQLAlchemy**: Database storage and ORM
- **Pandas/NumPy**: Data processing and analysis
- **OpenCV/scikit-learn**: Image processing for vehicle detection
- **Plotly/PyDeck**: Data visualization
- **Python-dotenv**: Environment variable management
- **RESTful APIs**: For integration with payment systems and external services

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- [Your Name]
- [Other Contributors]

## Acknowledgements

Special thanks to all contributors and supporters of this project.

# smart-parking
