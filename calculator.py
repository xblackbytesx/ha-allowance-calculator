"""Allowance calculation logic."""
import datetime
from typing import Tuple, Dict, Any


def calculate_age(birthday: datetime.date, reference_date: datetime.date = None) -> int:
    """Calculate age based on birthday."""
    if reference_date is None:
        reference_date = datetime.datetime.now().date()
    
    age = reference_date.year - birthday.year
    # Adjust age if birthday hasn't occurred yet this year
    if (reference_date.month, reference_date.day) < (birthday.month, birthday.day):
        age -= 1
    
    return age


def calculate_allowance(age: int, percentage: float = 30) -> float:
    """Calculate allowance based on age and percentage."""
    if age < 6:
        return 0.0
    
    return round(age * percentage / 100, 2)


def format_allowance(amount: float, currency: str = "EUR") -> str:
    """Format allowance with currency symbol."""
    from .const import SUPPORTED_CURRENCIES
    
    currency_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES["EUR"])
    symbol = currency_info["symbol"]
    
    if currency_info["position"] == "prefix":
        return f"{symbol}{amount:.2f}"
    else:
        return f"{amount:.2f}{symbol}"


def is_birthday(birthday: datetime.date, check_date: datetime.date = None) -> bool:
    """Check if today is the birthday."""
    if check_date is None:
        check_date = datetime.datetime.now().date()
    
    return birthday.month == check_date.month and birthday.day == check_date.day


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
    
    return {
        "name": name,
        "age": age,
        "allowance": allowance,
        "is_birthday": is_birthday_today,
        "next_age": age + 1 if is_birthday_today else age,
        "next_allowance": calculate_allowance(age + 1, percentage) if is_birthday_today else allowance,
    }
