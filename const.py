"""Constants for the Allowance Calculator integration."""
from typing import Dict, Any

DOMAIN = "allowance_calculator"

# Configuration
CONF_CHILDREN = "children"
CONF_BIRTHDAY = "birthday"
CONF_PERCENTAGE = "percentage"
CONF_CURRENCY = "currency"

# Defaults
DEFAULT_PERCENTAGE = 30
DEFAULT_CURRENCY = "EUR"
MIN_AGE_FOR_ALLOWANCE = 6
MAX_PERCENTAGE = 100
MIN_PERCENTAGE = 0

# Currency Settings
SUPPORTED_CURRENCIES = {
    "EUR": {"symbol": "€", "position": "prefix"},
    "USD": {"symbol": "$", "position": "prefix"},
    "GBP": {"symbol": "£", "position": "prefix"},
    "CAD": {"symbol": "C$", "position": "prefix"},
    "AUD": {"symbol": "A$", "position": "prefix"},
    "JPY": {"symbol": "¥", "position": "prefix"},
    "CHF": {"symbol": "CHF", "position": "suffix"},
    "SEK": {"symbol": "kr", "position": "suffix"},
    "NOK": {"symbol": "kr", "position": "suffix"},
    "DKK": {"symbol": "kr", "position": "suffix"},
}

# Icons
ICON = "mdi:cash"
ICON_BIRTHDAY = "mdi:cake-variant"

# Notification constants
NOTIFICATION_ID_PREFIX = "allowance_calculator_birthday"