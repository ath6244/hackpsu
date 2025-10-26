# Check-In Feature Setup ✅

## Status: WORKING

The attendance tracking system is now integrated and working.

### What's Been Done:

1. ✅ Created Flask backend (`app.py`) - Running on port 5000
2. ✅ Modified `attendancetracking.py` - Checks distance within 100m radius
3. ✅ Updated `StackedClassCard.jsx` - Shows "Check-in" button for current/upcoming classes
4. ✅ Integrated `LandingPage.jsx` - Makes API calls to Flask backend

### How It Works:

1. **User clicks "Check-in" button** on a class in the app
2. **React sends request** to Flask API at `http://localhost:5000/api/check-in`
3. **Flask backend**:
   - Gets user location (currently demo: ECore Building)
   - Calculates distance to class location
   - Returns success if within 100m radius
4. **User sees alert** with success/failure message

### Demo Location:
- Current user location: `(40.798404, -77.8605)` - ECore Building
- Geofence radius: **100 meters**

### Buildings Available:
- ECore Building, Penn State University
- Osmond Lab, Penn State University  
- Davey Lab, Penn State University
- Reber Building, Penn State University
- Thomas Building, Penn State University

### API Test:
```bash
curl -X POST http://localhost:5000/api/check-in \
  -H "Content-Type: application/json" \
  -d '{"classData": {"courseCode": "TEST", "location": "ECore Building, Penn State University, University Park, PA"}}'
```

### To Start the Services:

1. **Start Flask backend**:
   ```bash
   cd /Users/anuroopsaini/Documents/hackpsu
   source venv/bin/activate
   python app.py
   ```

2. **Start React frontend** (in another terminal):
   ```bash
   cd hackpsu
   npm run dev
   ```

3. **Access the app** at the React URL (usually http://localhost:5173)

### How to Use:
1. Open the app in browser
2. Look for classes marked "Now" or "Upcoming"
3. Click on a class card to expand it
4. Click the "Check-in" button
5. You'll see an alert with the result!

**Note**: The check-in button only appears for classes with status "current" or "upcoming" when the card is expanded.

