from vedastro import GeoLocation, Time
from datetime import datetime

def parse_user_input(input_str):
    """
    Parse input of format:
    'Name | HH:MM DD/MM/YYYY +TZ | City, Country, Longitude, Latitude'
    Example: 'Hare Krishna | 04:50 23/08/1996 +05:30 | New Delhi, India, 77.21, 28.61'
    """
    try:
        parts = [x.strip() for x in input_str.split('|')]
        if len(parts) != 3:
            raise ValueError("Expected format: 'Name | Time Info | Location Info'")

        name, time_part, location_part = parts

        # Validate time_part format (HH:MM DD/MM/YYYY +TZ)
        try:
            dt = datetime.strptime(time_part, "%H:%M %d/%m/%Y %z")
            print(f"✅ Parsed datetime: {dt.isoformat()}")
        except ValueError as ve:
            raise ValueError(f"Invalid datetime format. Expected 'HH:MM DD/MM/YYYY +TZ'. Error: {ve}")

        # Parse location
        location_parts = [x.strip() for x in location_part.split(',')]
        if len(location_parts) < 4:
            raise ValueError("Location must include city, country, longitude, latitude.")

        location_name = ', '.join(location_parts[:-2])
        longitude = float(location_parts[-2])
        latitude = float(location_parts[-1])

        geo = GeoLocation(location_name, longitude, latitude)
        vedic_time = Time(time_part, geo)

        print(f"👤 Name: {name}")
        print(f"🌐 Location: {location_name} | Lon: {longitude}, Lat: {latitude}")
        return name, vedic_time

    except Exception as e:
        raise ValueError(f"❌ Invalid input format: {e}")
