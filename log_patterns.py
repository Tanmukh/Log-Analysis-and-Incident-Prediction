from collections import defaultdict
import re
from datetime import datetime

class LogPatternRecognizer:
    def __init__(self, template_storage_path="log_templates.json"):
        self.templates = {}
        self.template_id_counter = 0
        self.template_storage_path = template_storage_path
        self._load_templates()

    def _load_templates(self):
        pass

    def _save_templates(self):
       
        pass

    def extract_template(self, message: str) -> (str, dict):
        """
        Extracts a general template from a log message.
        This is a simplified example. Real systems use more robust algorithms
        like Drain, Spell, or deep learning models for pattern extraction.
        """
        template = message
        template = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP_ADDR>', template) # IP addresses
        template = re.sub(r'\d+', '<NUM>', template) # Numbers
        template = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<UUID>', template) # UUIDs
        template = re.sub(r'[a-zA-Z0-9_-]+\.[a-zA-Z]{2,}', '<DOMAIN>', template) # Domains


        return template, {} 

    def process_log_event(self, parsed_event: dict) -> dict:
        """
        Identifies or creates a pattern for a given parsed log event.
        Adds a 'pattern_id' and 'template' to the event.
        """
        message = parsed_event.get('message', '')
        service_name = parsed_event.get('service_name', 'UNKNOWN')
        timestamp = parsed_event.get('timestamp', datetime.now())

        template, _ = self.extract_template(message)
        pattern_id = None

        for tid, data in self.templates.items():
            if data['template'] == template and data.get('service_name') == service_name:
                pattern_id = tid
                self.templates[tid]['count'] += 1
                self.templates[tid]['last_seen'] = timestamp
                break

        if pattern_id is None:
            self.template_id_counter += 1
            pattern_id = f"P{self.template_id_counter}"
            self.templates[pattern_id] = {
                'template': template,
                'count': 1,
                'first_seen': timestamp,
                'last_seen': timestamp,
                'service_name': service_name
            }

        parsed_event['pattern_id'] = pattern_id
        parsed_event['template'] = template
        return parsed_event
