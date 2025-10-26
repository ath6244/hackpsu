import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.insert(0, '.')
from attendancetracking import get_user_location, load_classes_from_ics, check_attendance

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

@app.route('/api/check-in', methods=['POST'])
def check_in():
    """Check-in API endpoint"""
    try:
        data = request.json
        class_data = data.get('classData')
        
        if not class_data:
            return jsonify({'error': 'No class data provided'}), 400
        
        # Get user's current location
        user_location = get_user_location()
        
        # Check attendance based on location
        result = check_attendance(class_data, user_location)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error during check-in: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)

