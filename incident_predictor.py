import joblib 
from datetime import datetime

class IncidentPredictionEngine:
    def __init__(self, model_path="incident_predictor_model.pkl"):
        self.prediction_models = {}
        self.active_anomalies = {}
        self.incident_rules = [
           
            {'name': 'DB_Connection_Exhaustion',
             'trigger_patterns': [('service_name', 'db-server-prod-03', 'ORA-00020_EXCEEDED'),
                                  ('service_name', 'api-gateway-us-east-01', 'connection_timeout')],
             'trigger_anomalies': ['Frequency Spike'],
             'min_concurrency': 2,
             'time_window_minutes': 10,
             'severity': 'CRITICAL',
             'predicted_impact': 'Database connection pool exhaustion leading to API Gateway latency spikes and service unavailability for user authentication.'
            },
           
        ]
        self.potential_incidents = {} 

    def _load_model(self, model_name):
       
        return None 

    def add_active_anomaly(self, anomaly_alert: dict):
        """Adds a newly detected anomaly to the active list."""
        anomaly_id = f"{anomaly_alert['type']}-{anomaly_alert['key']}-{anomaly_alert['timestamp']}"
        self.active_anomalies[anomaly_id] = anomaly_alert

    def clear_resolved_anomaly(self, anomaly_id: str):
        """Removes a resolved anomaly from the active list."""
        self.active_anomalies.pop(anomaly_id, None)

    def predict_incidents(self) -> list:
        """
        Evaluates active anomalies and patterns against predefined rules or ML models
        to predict incidents.
        This would be called periodically (e.g., every 30 seconds or minute).
        """
        predicted_incidents = []
        current_time = datetime.now()

        for rule in self.incident_rules:
            matched_triggers = []
            for trigger in rule['trigger_patterns']:
                for anomaly_id, anomaly_data in self.active_anomalies.items():
                    if 'key' in anomaly_data and isinstance(anomaly_data['key'], tuple):
                       
                        service_name, _, pattern_id = anomaly_data['key']
                        if (trigger[0] == 'service_name' and service_name == trigger[1] and
                            pattern_id and trigger[2] in pattern_id):
                            matched_triggers.append(anomaly_data)
                            break 
            
            for trigger_anomaly_type in rule.get('trigger_anomalies', []):
                for anomaly_id, anomaly_data in self.active_anomalies.items():
                    if anomaly_data['type'] == trigger_anomaly_type:
                        matched_triggers.append(anomaly_data)


            if len(matched_triggers) >= rule['min_concurrency']:
                first_match_time = min([m['timestamp'] for m in matched_triggers if 'timestamp' in m]) if matched_triggers else current_time
                if (current_time - first_match_time).total_seconds() / 60 <= rule['time_window_minutes']:

                    incident_key = f"{rule['name']}-{matched_triggers[0]['key']}" 
                    if incident_key not in self.potential_incidents or \
                       (current_time - self.potential_incidents[incident_key]['last_alert_time']).total_seconds() > 300: 

                        predicted_incident = {
                            'alert_id': f"PRED-{current_time.strftime('%Y%m%d-%H%M%S')}",
                            'timestamp': current_time,
                            'severity': rule['severity'],
                            'likelihood': 'High' if len(matched_triggers) >= rule['min_concurrency'] else 'Medium', 
                            'predicted_impact': rule['predicted_impact'],
                            'component_s_affected': list(set([m['key'][0] for m in matched_triggers if isinstance(m['key'], tuple)])),
                            'root_cause_analysis_predicted': f"Rule '{rule['name']}' triggered by {len(matched_triggers)} matched patterns/anomalies.",
                            'contextual_data': {
                                'active_anomalies_matched': [anom['key'] for anom in matched_triggers],
                            },
                            'recommended_actions': ["Review relevant service logs immediately.", "Escalate to on-call team.", "Check system dashboards for affected components."],
                            'rule_name': rule['name']
                        }
                        predicted_incidents.append(predicted_incident)
                        self.potential_incidents[incident_key] = {
                            'last_alert_time': current_time,
                            'details': predicted_incident
                        }

        return predicted_incidents
