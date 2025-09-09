from datetime import datetime


def format_date(value):
    """Format a datetime object to a readable date string."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.strftime("%Y-%m-%d %H:%M")
