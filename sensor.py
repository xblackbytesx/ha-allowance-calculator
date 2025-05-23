"""Sensor platform for allowance calculator."""
import logging
import datetime
from typing import Optional, List

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.const import CONF_NAME, CONF_CURRENCY

from .const import (
    DOMAIN,
    CONF_CHILDREN,
    CONF_BIRTHDAY,
    CONF_PERCENTAGE,
    DEFAULT_PERCENTAGE,
    DEFAULT_CURRENCY,
    ICON,
)
from .calculator import calculate_age, calculate_allowance, format_allowance

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Allowance Calculator sensor from a config entry."""
    if config_entry.entry_id not in hass.data[DOMAIN]:
        return

    config_data = hass.data[DOMAIN][config_entry.entry_id]
    children = config_data.get(CONF_CHILDREN, [])
    currency = config_data.get(CONF_CURRENCY, DEFAULT_CURRENCY)
    
    sensors = []
    for child in children:
        sensors.append(AllowanceSensor(child, currency))
    
    async_add_entities(sensors, True)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None
) -> None:
    """Set up the Allowance Calculator sensor from YAML configuration."""
    if DOMAIN not in hass.data:
        return
    
    children = hass.data[DOMAIN].get("children", [])
    currency = hass.data[DOMAIN].get("currency", DEFAULT_CURRENCY)
    
    sensors = []
    for child in children:
        sensors.append(AllowanceSensor(child, currency))
    
    async_add_entities(sensors, True)


class AllowanceSensor(SensorEntity):
    """Representation of an Allowance sensor."""

    def __init__(self, child_config, currency):
        """Initialize the sensor."""
        self._name = child_config[CONF_NAME]
        self._birthday = datetime.datetime.strptime(
            child_config[CONF_BIRTHDAY], "%Y-%m-%d"
        ).date()
        self._percentage = child_config.get(CONF_PERCENTAGE, DEFAULT_PERCENTAGE)
        self._currency = currency
        self._state = None
        self._attributes = {}
        
        # Entity properties
        self._attr_has_entity_name = True
        self._attr_name = f"{self._name}'s Allowance"
        self._attr_unique_id = f"allowance_{self._name.lower()}"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = self._currency
        self._attr_icon = ICON
        
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name
        
    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self) -> dict:
        """Return device specific state attributes."""
        return self._attributes
        
    async def async_update(self) -> None:
        """Update the sensor."""
        now = datetime.datetime.now().date()
        age = calculate_age(self._birthday, now)
        allowance = calculate_allowance(age, self._percentage)
        
        self._state = allowance
        self._attributes = {
            "age": age,
            "birthday": self._birthday.strftime("%Y-%m-%d"),
            "percentage": self._percentage,
            "formatted_value": format_allowance(allowance, self._currency),
            "days_until_birthday": self._days_until_birthday(now),
            "next_allowance": calculate_allowance(age + 1, self._percentage) if self._is_birthday(now) else allowance,
        }
        
    def _is_birthday(self, current_date: datetime.date) -> bool:
        """Check if today is the birthday."""
        return self._birthday.month == current_date.month and self._birthday.day == current_date.day
        
    def _days_until_birthday(self, current_date: datetime.date) -> int:
        """Calculate days until next birthday."""
        next_birthday = datetime.date(
            current_date.year + (1 if current_date.month > self._birthday.month or 
                               (current_date.month == self._birthday.month and 
                                current_date.day >= self._birthday.day) else 0),
            self._birthday.month,
            self._birthday.day
        )
        return (next_birthday - current_date).days
