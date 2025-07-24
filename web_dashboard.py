from flask import Flask, render_template, jsonify
from datetime import datetime
from log_patterns import LogPatternRecognizer
from anomaly_detector import AnomalyDetector
from incident_predictor import IncidentPredictionEngine
from alerting_system import AlertingSystem

app = Flask(__name__)

raw_logs = [
    '2025-07-04 12:00:01 [INFO] web-server-1 - User 123 logged in from 192.168.1.100',
    '2025-07-04 12:00:05 [ERROR] db-service-prod - Failed to connect to DB on port 5432. Error code 101.',
    '2025-07-04 12:00:10 [INFO] web-server-1 - User 456 logged in from 192.168.1.101',
    '2025-07-04 12:00:15 [DEBUG] message-queue-worker - Processing message <UUID> completed successfully in 15ms.',
    '2025-07-04 12:00:20 [ERROR] db-service-prod - Failed to connect to DB on port 5432. Error code 101.'
]

def parse_simple_log(log_line: str) -> dict:
    parts = log_line.split(' ', 4)
    timestamp_str = f"{parts[0]} {parts[1]}"
    log_level = parts[2].strip('[]')
    service_name = parts[3].strip('- ')
    message = parts[4]
    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        timestamp = datetime.now()
    return {
        'timestamp': timestamp,
        'log_level': log_level,
        'service_name': service_name,
        'message': message
    }


pattern_recognizer = LogPatternRecognizer()
anomaly_detector = AnomalyDetector(window_size=5, history_size=10)
prediction_engine = IncidentPredictionEngine()
alerting_system = AlertingSystem()

@app.route('/')
def index():
    parsed_events = [parse_simple_log(log) for log in raw_logs]
    processed_events = [pattern_recognizer.process_log_event(e) for e in parsed_events]
    for event in processed_events:
        anomaly_detector.update_counts(event)
    anomalies = anomaly_detector.detect_anomalies_in_window()
    for anomaly in anomalies:
        anomaly['timestamp'] = datetime.now()
        prediction_engine.add_active_anomaly(anomaly)
    predicted_incidents = prediction_engine.predict_incidents()
    for incident in predicted_incidents:
        alerting_system.send_alert(incident)
    return render_template('dashboard.html',
                           logs=processed_events,
                           anomalies=anomalies,
                           incidents=predicted_incidents)

@app.route('/api/logs')
def api_logs():
    parsed_events = [parse_simple_log(log) for log in raw_logs]
    processed_events = [pattern_recognizer.process_log_event(e) for e in parsed_events]
    return jsonify(processed_events)

@app.route('/api/anomalies')
def api_anomalies():
    return jsonify(anomaly_detector.detect_anomalies_in_window())

@app.route('/api/incidents')
def api_incidents():
    incidents = prediction_engine.predict_incidents()
    return jsonify(incidents)

if __name__ == '__main__':
    app.run(debug=True)
