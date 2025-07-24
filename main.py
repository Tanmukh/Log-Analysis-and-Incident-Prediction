from log_patterns import LogPatternRecognizer
from datetime import datetime
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

parsed_events = [parse_simple_log(log) for log in raw_logs]

print("--- Log Pattern Recognition ---")
pattern_recognizer = LogPatternRecognizer()
processed_events_with_patterns = []
for event in parsed_events:
    processed_event = pattern_recognizer.process_log_event(event)
    processed_events_with_patterns.append(processed_event)
    print(f"Original: {event['message']} -> Pattern ID: {processed_event['pattern_id']} (Template: {processed_event['template']})")

print("\n--- Identified Templates ---")
for pid, data in pattern_recognizer.templates.items():
    print(f"ID: {pid}, Template: {data['template']}, Count: {data['count']}")

from anomaly_detector import AnomalyDetector
print("\n--- Anomaly Detection (Conceptual) ---")
anomaly_detector = AnomalyDetector(window_size=5, history_size=10)

for event in processed_events_with_patterns:
    anomaly_detector.update_counts(event)

anomalies = anomaly_detector.detect_anomalies_in_window()
if anomalies:
    print("\nDetected Anomalies:")
    for anomaly in anomalies:
        print(f"- {anomaly['type']} for {anomaly['key']} (Severity: {anomaly['severity']})")
else:
    print("No immediate anomalies detected in this simulated window.")

from incident_predictor import IncidentPredictionEngine 
from alerting_system import AlertingSystem 

print("\n--- Incident Prediction (Conceptual) ---")
prediction_engine = IncidentPredictionEngine()
alerting_system = AlertingSystem() 

if anomalies:
    for anomaly in anomalies:
        anomaly['timestamp'] = datetime.now()
        prediction_engine.add_active_anomaly(anomaly)

predicted_incidents = prediction_engine.predict_incidents()
if predicted_incidents:
    print("\n--- Predicted Incidents ---")
    for incident in predicted_incidents:
        alerting_system.send_alert(incident)
else:
    print("No incidents predicted based on current active anomalies.")