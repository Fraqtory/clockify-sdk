"""
Date and time utility functions
"""

from datetime import datetime, timezone, timedelta
from typing import Tuple
import calendar


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


def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object to ISO 8601 format with UTC timezone

    Args:
        dt: Datetime object to format

    Returns:
        ISO 8601 formatted string with UTC timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # Set timezone to UTC if naive
    else:
        dt = dt.astimezone(timezone.utc)  # Convert to UTC if already timezone-aware
    return dt.isoformat().replace("+00:00", "Z")


def get_last_month_range() -> Tuple[datetime, datetime]:
    """
    Get the start and end dates of the previous month.
    
    Returns:
        Tuple of (start_date, end_date) for the previous month
    """
    current_date = datetime.now(timezone.utc)
    
    # Get the first day of the current month
    first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Subtract one day to get the last day of the previous month
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    
    # Get the first day of the previous month
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    # Set end date to end of the last day of previous month
    end_date = last_day_previous_month.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return first_day_previous_month, end_date


def get_last_week_range() -> Tuple[datetime, datetime]:
    """
    Get the start and end dates of the previous week (Monday to Sunday).
    
    Returns:
        Tuple of (start_date, end_date) for the previous week
    """
    current_date = datetime.now(timezone.utc)
    
    # Get the start of the current week (Monday)
    current_week_start = get_week_start(current_date)
    
    # Subtract 7 days to get the start of the previous week
    last_week_start = current_week_start - timedelta(days=7)
    
    # Get the end of the previous week (Sunday)
    last_week_end = last_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    
    return last_week_start, last_week_end


def get_week_start(date: datetime) -> datetime:
    """
    Get the Monday of the week for a given date.
    
    Args:
        date: The date to get the week start for
        
    Returns:
        Monday of the week containing the given date
    """
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)


def get_month_range(year: int, month: int) -> Tuple[datetime, datetime]:
    """
    Get the start and end dates of a specific month.
    
    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        
    Returns:
        Tuple of (start_date, end_date) for the specified month
    """
    # Get the first day of the month
    first_day = datetime(year, month, 1, tzinfo=timezone.utc)
    
    # Get the last day of the month
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num, 23, 59, 59, 999999, tzinfo=timezone.utc)
    
    return first_day, last_day


def get_week_range(year: int, week: int) -> Tuple[datetime, datetime]:
    """
    Get the start and end dates of a specific week.
    
    Args:
        year: Year (e.g., 2024)
        week: Week number (1-53)
        
    Returns:
        Tuple of (start_date, end_date) for the specified week
    """
    # Get the Monday of the specified week
    jan_4 = datetime(year, 1, 4, tzinfo=timezone.utc)  # Jan 4 is always in week 1
    week_start = jan_4 + timedelta(weeks=week-1)
    week_start = week_start - timedelta(days=week_start.weekday())  # Get Monday
    
    # Get the Sunday of the week
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    
    return week_start, week_end


def count_weeks_in_range(start_date: datetime, end_date: datetime) -> float:
    """
    Count the number of weeks (including partial weeks) in a date range.
    
    Args:
        start_date: Start date of the range
        end_date: End date of the range
        
    Returns:
        Number of weeks as a float (e.g., 2.5 for 2.5 weeks)
    """
    # Calculate the total duration in days
    total_days = (end_date - start_date).total_seconds() / (24 * 3600)
    
    # Convert to weeks (7 days = 1 week)
    weeks = total_days / 7.0
    
    return weeks
