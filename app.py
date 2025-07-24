from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import datetime
import json

app = Flask(__name__)
CORS(app)

# Initialize Firebase
cred = credentials.Certificate('path/to/serviceAccountKey.json')  # Replace with your Firebase service account key path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-firebase-project.firebaseio.com/'  # Replace with your Firebase URL
})

@app.route('/')
def index():
    return render_template('index.html')  # Placeholder; use patient.html or doctor.html based on route

@app.route('/patient')
def patient():
    return send_file('patient.html')

@app.route('/doctor')
def doctor():
    return send_file('doctor.html')

@app.route('/upload_vitals', methods=['POST'])
def upload_vitals():
    try:
        data = request.get_json()
        if not all(k in data for k in ['patientId', 'spo2', 'temp', 'hr']):
            return jsonify({'error': 'Missing required fields'}), 400
        ref = db.reference(f'/vitals/{data["patientId"]}')
        data['timestamp'] = datetime.datetime.now().isoformat()
        ref.push(data)
        return jsonify({'message': 'Vitals uploaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_vitals', methods=['GET'])
def get_vitals():
    try:
        ref = db.reference('/vitals')
        vitals = ref.get()
        if not vitals:
            return jsonify({'vitals': []})
        # Flatten the nested structure
        all_vitals = []
        for patient_id, records in vitals.items():
            for key, value in records.items():
                all_vitals.append({
                    'patientId': patient_id,
                    'timestamp': value['timestamp'],
                    'spo2': value['spo2'],
                    'temp': value['temp'],
                    'hr': value['hr']
                })
        return jsonify({'vitals': all_vitals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
