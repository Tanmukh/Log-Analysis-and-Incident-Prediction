import re
from datetime import datetime

def parse_log_event(raw_log_line: str) -> dict:
    """
    Parses a raw log line into a structured dictionary.
    This would typically use a library like `re` for regex, or a more
    sophisticated log parser.
    """
    parsed_data = {}
    try:
        if "nginx" in raw_log_line:
            match = re.search(r'(\\d{2}/\\w{3}/\\d{4}:\\d{2}:\\d{2}:\\d{2} \\+\\d{4}) "([A-Z]+) (.+?) HTTP/\\d\\.\\d" (\\d{3}) (\\d+)', raw_log_line)
            if match:
                parsed_data['timestamp'] = datetime.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S %z")
                parsed_data['service_name'] = 'nginx'
                parsed_data['log_level'] = 'INFO' if 200 <= int(match.group(4)) < 400 else 'ERROR'
                parsed_data['http_method'] = match.group(2)
                parsed_data['request_path'] = match.group(3)
                parsed_data['status_code'] = int(match.group(4))
                parsed_data['bytes_sent'] = int(match.group(5))
                parsed_data['message'] = f"Request {match.group(3)} returned {match.group(4)}"
        elif "java" in raw_log_line and "OutOfMemoryError" in raw_log_line:
            match = re.search(r'(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3}) \\[(\\w+)\\] (.+?) - (.*)', raw_log_line)
            if match:
                parsed_data['timestamp'] = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S,%f")
                parsed_data['log_level'] = match.group(2)
                parsed_data['service_name'] = match.group(3)
                parsed_data['message'] = match.group(4)
                parsed_data['error_type'] = 'OutOfMemoryError'
        else:
            parsed_data['timestamp'] = datetime.now() 
            parsed_data['log_level'] = 'UNKNOWN'
            parsed_data['service_name'] = 'UNKNOWN'
            parsed_data['message'] = raw_log_line
    except Exception as e:
        print(f"Error parsing log: {e} - {raw_log_line}")
        parsed_data = {
            'timestamp': datetime.now(),
            'log_level': 'PARSE_ERROR',
            'service_name': 'SYSTEM',
            'message': f"Failed to parse: {raw_log_line}"
        }
    return parsed_data

