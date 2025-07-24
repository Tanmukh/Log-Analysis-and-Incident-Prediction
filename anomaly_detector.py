from collections import deque, defaultdict
import numpy as np

class AnomalyDetector:
    def __init__(self, window_size=60, z_score_threshold=3.0, history_size=1000):
        self.metrics_history = defaultdict(lambda: deque(maxlen=history_size))
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.current_window_counts = defaultdict(int) 

    def update_counts(self, parsed_event: dict):
        """Aggregates counts for the current time window."""
        key = (parsed_event.get('service_name'), parsed_event.get('log_level'), parsed_event.get('pattern_id'))
        self.current_window_counts[key] += 1

    def detect_anomalies_in_window(self) -> list:
        """
        Detects anomalies based on the counts accumulated in the current window.
        This method would be called periodically (e.g., every minute) by the stream processor.
        """
        anomalies = []
        for key, current_count in self.current_window_counts.items():
            history = self.metrics_history[key]

            
            history.append(current_count)

            if len(history) >= self.window_size: 
                mean = np.mean(list(history)[-self.window_size:])
                std_dev = np.std(list(history)[-self.window_size:])

                if std_dev == 0:
                    if current_count > mean and mean > 0: 
                        anomalies.append({
                            'type': 'Frequency Spike',
                            'key': key,
                            'current_count': current_count,
                            'baseline_mean': mean,
                            'severity': 'Medium' if current_count > mean * 2 else 'Low', 
                            'details': f"Constant baseline, sudden spike to {current_count}"
                        })
                    continue

                z_score = (current_count - mean) / std_dev

                if abs(z_score) > self.z_score_threshold:
                    severity = 'High' if abs(z_score) > self.z_score_threshold * 1.5 else 'Medium'
                    anomaly_type = "High Frequency" if z_score > 0 else "Low Frequency"
                    anomalies.append({
                        'type': anomaly_type,
                        'key': key,
                        'current_count': current_count,
                        'baseline_mean': mean,
                        'z_score': z_score,
                        'severity': severity,
                        'details': f"Z-score {z_score:.2f} for {key} count {current_count}"
                    })

       
        self.current_window_counts.clear()
        return anomalies
