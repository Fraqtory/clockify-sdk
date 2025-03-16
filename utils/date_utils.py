from datetime import datetime, timezone

def format_date(date: datetime) -> str:
    """
    Format a datetime object as a string for Clockify API

    Args:
        date: Datetime object to format

    Returns:
        ISO 8601 formatted UTC time string with Z suffix
    """
    return date.isoformat().replace("+00:00", "Z")

def get_current_utc_time() -> str:
    """
    Get current UTC time formatted for Clockify API

    Returns:
        ISO 8601 formatted UTC time string with Z suffix
    """
    return format_date(datetime.now(timezone.utc)) 