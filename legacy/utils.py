
from datetime import datetime

def extract_dob(input_str: str) -> str:
    """
    Extracts DOB in YYYY-MM-DD format from the input string:
    'Name | HH:MM DD/MM/YYYY +TZ | City, Country, Longitude, Latitude'
    """
    try:
        parts = [p.strip() for p in input_str.split('|')]
        if len(parts) < 2:
            raise ValueError("Invalid input format.")

        time_part = parts[1]
        # Parse using datetime with timezone
        dt = datetime.strptime(time_part, "%H:%M %d/%m/%Y %z")
        return dt.date().isoformat()  # returns 'YYYY-MM-DD'
    except Exception as e:
        raise ValueError(f"Error extracting DOB: {e}")
    