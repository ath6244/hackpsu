# Backend Setup for Attendance Tracking

## Quick Start

### 1. Start the Flask Backend Server

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The server will run on `http://localhost:5000`

### 2. Start the React Frontend

```bash
cd hackpsu
npm install  # if not already installed
npm run dev
```

## API Endpoints

### Check-in Endpoint
- **URL**: `http://localhost:5000/api/check-in`
- **Method**: POST
- **Body**: 
  ```json
  {
    "classData": {
      "courseCode": "CMPSC 311",
      "location": "ECore Building, Penn State University, University Park, PA",
      "startTime": "...",
      "endTime": "..."
    }
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "distance": 45.2,
    "message": "Check-in successful! You are 45.2m from ECore Building, Penn State University, University Park, PA"
  }
  ```

### Health Check
- **URL**: `http://localhost:5000/api/health`
- **Method**: GET

## How It Works

1. User clicks "Check-in" button on a current class in the React app
2. React sends POST request to Flask backend with class data
3. Flask backend:
   - Gets user's current location (currently returns demo coordinates)
   - Checks distance from user to class location
   - If within 100m radius, attendance is marked
4. Response is sent back to React app with success/failure message

## Notes

- Currently uses demo location: (40.798404, -77.8605) - ECore Building
- Geofence radius: 100 meters
- To enable real location tracking, update `get_user_location()` in `attendancetracking.py`

