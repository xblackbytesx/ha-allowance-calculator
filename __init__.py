"""The Allowance Calculator integration."""
import asyncio
import datetime
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import Platform, CONF_NAME, CONF_CURRENCY
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import event
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_CHILDREN,
    CONF_BIRTHDAY,
    CONF_PERCENTAGE,
    DEFAULT_PERCENTAGE,
    DEFAULT_CURRENCY,
    SUPPORTED_CURRENCIES,
)
from .calculator import get_child_allowance_data, format_allowance

_LOGGER = logging.getLogger(__name__)

CHILD_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_BIRTHDAY): cv.string,
    vol.Optional(CONF_PERCENTAGE, default=DEFAULT_PERCENTAGE): vol.Coerce(float),
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_CHILDREN): vol.All(cv.ensure_list, [CHILD_SCHEMA]),
        vol.Optional(CONF_CURRENCY, default=DEFAULT_CURRENCY): vol.In(list(SUPPORTED_CURRENCIES.keys())),
    })
}, extra=vol.ALLOW_EXTRA)

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Set up the Allowance Calculator component."""
    if DOMAIN not in config:
        return True

    domain_config = config[DOMAIN]
    children = domain_config[CONF_CHILDREN]
    currency = domain_config.get(CONF_CURRENCY, DEFAULT_CURRENCY)

    hass.data[DOMAIN] = {
        "children": children,
        "currency": currency,
    }

    async def update_allowances(now=None):
        """Update allowances for all children."""
        if now is None:
            now = datetime.datetime.now()
        
        current_date = now.date()
        
        for child in children:
            child_data = get_child_allowance_data(child, current_date)
            name = child_data["name"]
            allowance = child_data["allowance"]
            
            # Update state
            hass.states.async_set(
                f"sensor.{name.lower()}_allowance",
                allowance,
                {
                    "friendly_name": f"{name}'s Allowance",
                    "unit_of_measurement": currency,
                    "formatted_value": format_allowance(allowance, currency),
                    "age": child_data["age"],
                    "percentage": child.get(CONF_PERCENTAGE, DEFAULT_PERCENTAGE),
                }
            )
            
            # Check if it's the child's birthday
            if child_data["is_birthday"]:
                new_allowance = child_data["next_allowance"]
                _LOGGER.info(f"It's {name}'s birthday! New allowance: {format_allowance(new_allowance, currency)}")
                
                hass.components.persistent_notification.async_create(
                    f"It's {name}'s birthday! New weekly allowance: {format_allowance(new_allowance, currency)}",
                    title=f"Allowance Update for {name}"
                )

    # Schedule daily updates at midnight
    @callback
    def schedule_midnight_update(now=None):
        """Schedule next update at midnight."""
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow, datetime.time())
        
        event.async_track_point_in_time(
            hass, 
            lambda x: asyncio.create_task(update_allowances(x)),
            next_midnight
        )
        
        # Also schedule the next update
        event.async_track_point_in_time(
            hass,
            schedule_midnight_update,
            next_midnight
        )

    # Initial update
    await update_allowances()
    
    # Schedule the first midnight update
    schedule_midnight_update()
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Allowance Calculator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
