import requests 
import json
from datetime import datetime

class AlertingSystem:
    def __init__(self, slack_webhook_url=None, pagerduty_api_key=None):
        self.slack_webhook_url = slack_webhook_url
        self.pagerduty_api_key = pagerduty_api_key
        self.sent_alerts_cache = {} 

    def _format_slack_message(self, alert: dict) -> dict:
        color_map = {
            'CRITICAL': '#FF0000',
            'HIGH': '#FFA500',
            'MEDIUM': '#FFFF00',
            'LOW': '#00BFFF',
            'INFO': '#ADD8E6',
            'RESOLVED': '#00FF00'
        }
        color = color_map.get(alert.get('severity', 'INFO').upper(), '#CCCCCC')

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {alert.get('severity', 'INFO').upper()} ALERT: {alert.get('rule_name', 'Predicted Incident')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Alert ID:*\n`{alert.get('alert_id')}`"},
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n{alert.get('timestamp').strftime('%Y-%m-%d %H:%M:%S IST')}"},
                    {"type": "mrkdwn", "text": f"*Likelihood:*\n{alert.get('likelihood', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Components Affected:*\n`{', '.join(alert.get('component_s_affected', ['N/A']))}`"},
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Predicted Impact:*\n{alert.get('predicted_impact', 'N/A')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause Analysis (Predicted):*\n{alert.get('root_cause_analysis_predicted', 'N/A')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Contextual Data:*\n```json\n{json.dumps(alert.get('contextual_data', {}), indent=2)}\n```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommended Actions:*\n• {chr(10) + '• '.join(alert.get('recommended_actions', ['No specific actions provided.']))}"
                }
            },
            {"type": "divider"}
        ]
        return {"blocks": blocks, "attachments": [{"color": color}]}

    def send_alert(self, alert: dict):
        alert_id = alert.get('alert_id')
        severity = alert.get('severity', 'INFO').upper()
        current_time = datetime.now()
        if alert_id in self.sent_alerts_cache and \
           (current_time - self.sent_alerts_cache[alert_id]).total_seconds() < 300:
            print(f"Suppressing duplicate alert: {alert_id}")
            return

        self.sent_alerts_cache[alert_id] = current_time
        print(f"\n--- Sending Alert: {alert_id} ({severity}) ---")
        print(json.dumps(alert, indent=2, default=str)) 

        if severity == 'CRITICAL' and self.pagerduty_api_key:
            
            print("PagerDuty alert (simulated)")

        if self.slack_webhook_url and severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            slack_message = self._format_slack_message(alert)
           
            print("Slack alert (simulated)")
