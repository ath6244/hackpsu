from datetime import datetime
from geopy.distance import geodesic
from ics import Calendar
import pytz

# -----------------------------
# Config
# -----------------------------
ICS_FILE = "demo-oct25.ics"
RADIUS_METERS = 100       # geofence radius
NY_TZ = pytz.timezone("America/New_York")

# -----------------------------
# Accurate PSU building coordinates
# -----------------------------
BUILDING_COORDS = {
    "ECore Building, Penn State University, University Park, PA": (40.798404, -77.8605),
    "Osmond Lab, Penn State University, University Park, PA": (40.79692, -77.8726),
    "Davey Lab, Penn State University, University Park, PA": (40.797905, -77.862364),
    "Reber Building, Penn State University, University Park, PA": (40.7934794, -77.8644466),
    "Thomas Building, Penn State University, University Park, PA": (40.800482, -77.860418),
}

# -----------------------------
# Replace this with actual current coordinates
# -----------------------------
def get_user_location():
    # Example: you are sitting in ECore
    return (40.798404, -77.8605)

# -----------------------------
# Functions
# -----------------------------
def get_coordinates(location):
    return BUILDING_COORDS.get(location, None)

def load_classes_from_ics(file_path):
    with open(file_path, 'r') as f:
        calendar = Calendar(f.read())

    classes = []
    for event in calendar.events:
        start = event.begin.datetime
        end = event.end.datetime

        # Ensure timezone-aware
        if start.tzinfo is None:
            start = NY_TZ.localize(start)
        if end.tzinfo is None:
            end = NY_TZ.localize(end)

        classes.append({
            "name": event.name,
            "location": event.location,
            "start": start,
            "end": end,
        })

    # Sort classes by start time
    return sorted(classes, key=lambda x: x["start"])

def check_attendance(class_data, user_location):
    """
    Check if user is within geofence of class location.
    
    Args:
        class_data: Dict with keys like 'location', 'courseCode', etc.
        user_location: Tuple of (lat, lon)
    
    Returns:
        dict with 'success' (bool), 'distance' (float), 'message' (str)
    """
    location = class_data.get('location', '')
    course_code = class_data.get('courseCode', 'Unknown')
    
    print(f"\n📍 Checking attendance for {course_code} ({location})")

    class_coords = get_coordinates(location)
    if not class_coords:
        print(f"❌ Skipping {course_code} — invalid coordinates.")
        return {
            'success': False,
            'distance': None,
            'message': f'Location "{location}" not found in coordinates database.'
        }

    distance = geodesic(user_location, class_coords).meters
    if distance <= RADIUS_METERS:
        print(f"🎉 User is inside geofence ({distance:.1f} m) — Attendance marked!")
        return {
            'success': True,
            'distance': round(distance, 1),
            'message': f'Check-in successful! You are {distance:.1f}m from {location}'
        }
    else:
        print(f"❌ User is outside geofence ({distance:.1f} m) — Attendance not marked.")
        return {
            'success': False,
            'distance': round(distance, 1),
            'message': f'You are {distance:.1f}m away from {location}. Please move closer to check in.'
        }

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    classes = load_classes_from_ics(ICS_FILE)
    user_location = get_user_location()
    
    print(f"📅 Loaded {len(classes)} classes from {ICS_FILE}")
    print(f"📍 User location: {user_location}")
    
    # Check attendance for each class
    for class_info in classes:
        check_attendance(class_info, user_location)
