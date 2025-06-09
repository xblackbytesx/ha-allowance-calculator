"""Allowance calculation logic."""
import datetime
from typing import Tuple, Dict, Any
from .const import MIN_AGE_FOR_ALLOWANCE


def calculate_age(birthday: datetime.date, reference_date: datetime.date = None) -> int:
    """Calculate age based on birthday."""
    if reference_date is None:
        reference_date = datetime.datetime.now().date()
    
    if birthday > reference_date:
        raise ValueError("Birthday cannot be in the future")
    
    age = reference_date.year - birthday.year
    # Adjust age if birthday hasn't occurred yet this year
    if (reference_date.month, reference_date.day) < (birthday.month, birthday.day):
        age -= 1
    
    return max(0, age)


def calculate_allowance(age: int, percentage: float = 30) -> float:
    """Calculate allowance based on age and percentage."""
    if age < MIN_AGE_FOR_ALLOWANCE:
        return 0.0
    
    # Ensure percentage is within valid range
    percentage = max(0, min(100, percentage))
    
    return round(age * percentage / 100, 2)


def get_child_allowance_data(
    child_config: Dict[str, Any], current_date: datetime.date = None
) -> Dict[str, Any]:
    """Calculate allowance data for a child."""
    if current_date is None:
        current_date = datetime.datetime.now().date()
    
    name = child_config["name"]
    birthday = datetime.datetime.strptime(child_config["birthday"], "%Y-%m-%d").date()
    percentage = child_config.get("percentage", 30)
    
    age = calculate_age(birthday, current_date)
    allowance = calculate_allowance(age, percentage)
    is_birthday_today = is_birthday(birthday, current_date)
    
    # Calculate next allowance (what they'll get after next birthday)
    next_age = age + 1
    next_allowance = calculate_allowance(next_age, percentage)
    
    return {
        "name": name,
        "age": age,
        "allowance": allowance,
        "is_birthday": is_birthday_today,
        "next_age": next_age,
        "next_allowance": next_allowance,
        "percentage": percentage,
        "birthday": birthday.strftime("%Y-%m-%d"),
    }


def format_allowance(amount: float, currency: str = "EUR") -> str:
    """Format allowance with currency symbol."""
    from .const import SUPPORTED_CURRENCIES
    
    currency_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES["EUR"])
    symbol = currency_info["symbol"]
    
    if currency_info["position"] == "prefix":
        return f"{symbol}{amount:.2f}"
    else:
        return f"{amount:.2f} {symbol}"


def is_birthday(birthday: datetime.date, check_date: datetime.date = None) -> bool:
    """Check if today is the birthday."""
    if check_date is None:
        check_date = datetime.datetime.now().date()
    
    return birthday.month == check_date.month and birthday.day == check_date.day


def validate_birthday(birthday_str: str) -> bool:
    """Validate birthday format and ensure it's not in the future."""
    try:
        birthday = datetime.datetime.strptime(birthday_str, "%Y-%m-%d").date()
        return birthday <= datetime.date.today()
    except ValueError:
        return False


def validate_percentage(percentage: float) -> bool:
    """Validate percentage is within acceptable range."""
    return 0 <= percentage <= 100