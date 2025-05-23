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

# Currency Settings
SUPPORTED_CURRENCIES = {
    "EUR": {"symbol": "€", "position": "prefix"},
    "USD": {"symbol": "$", "position": "prefix"},
    "GBP": {"symbol": "£", "position": "prefix"},
}

# Icons
ICON = "mdi:cash"
