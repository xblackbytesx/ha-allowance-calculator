"""Sensor platform for allowance calculator."""
import logging
import datetime
from typing import Optional, List

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_CHILDREN,
    CONF_BIRTHDAY,
    CONF_PERCENTAGE,
    DEFAULT_PERCENTAGE,
    DEFAULT_CURRENCY,
    ICON,
    ICON_BIRTHDAY,
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
    currency = config_data.get("currency", DEFAULT_CURRENCY)
    
    sensors = []
    for child in children:
        sensors.append(AllowanceSensor(child, currency, config_entry.entry_id))
        sensors.append(BirthdayCountdownSensor(child, config_entry.entry_id))
    
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
        sensors.append(BirthdayCountdownSensor(child))
    
    async_add_entities(sensors, True)


class AllowanceSensor(SensorEntity):
    """Representation of an Allowance Calculator sensor."""

    def __init__(self, child_config, currency, entry_id=None):
        """Initialize the sensor."""
        self._name = child_config[CONF_NAME]
        try:
            self._birthday = datetime.datetime.strptime(
                child_config[CONF_BIRTHDAY], "%Y-%m-%d"
            ).date()
        except ValueError as e:
            _LOGGER.error(f"Invalid date format for {self._name}: {child_config[CONF_BIRTHDAY]}")
            raise e
            
        self._percentage = max(0, min(100, child_config.get(CONF_PERCENTAGE, DEFAULT_PERCENTAGE)))
        self._currency = currency
        self._entry_id = entry_id
        self._state = None
        self._attributes = {}
        
        clean_name = self._name.lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        
        # HOME ASSISTANT STANDARD WAY
        self._attr_has_entity_name = True
        self._attr_name = "Allowance"
        self._attr_unique_id = f"allowance_{clean_name}"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = self._currency
        self._attr_icon = ICON
        
    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information."""
        if self._entry_id:
            clean_name = self._name.lower().replace(' ', '_')
            return DeviceInfo(
                identifiers={(DOMAIN, f"{self._entry_id}_{clean_name}")},
                name=self._name,  # This becomes the device name
                manufacturer="Allowance Calculator",
                model="Child Tracker",
                sw_version="1.0.0",
            )
        return None
        
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
        
    def update(self):
        """Update the sensor."""
        try:
            age = calculate_age(self._birthday)
            allowance = calculate_allowance(age, self._percentage)
            next_age = age + 1 if self._is_birthday_today() else age + 1
            next_allowance = calculate_allowance(next_age, self._percentage)
            
            self._state = allowance
            self._attributes = {
                "age": age,
                "birthday": self._birthday.strftime("%Y-%m-%d"),
                "percentage": self._percentage,
                "formatted_value": format_allowance(allowance, self._currency),
                "days_until_birthday": self._days_until_birthday(),
                "next_allowance": next_allowance,
                "currency": self._currency,
                "is_birthday_today": self._is_birthday_today(),
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating sensor for {self._name}: {e}")
            
    def _days_until_birthday(self):
        """Calculate days until next birthday."""
        today = datetime.date.today()
        next_birthday = self._birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days
        
    def _is_birthday_today(self):
        """Check if today is the birthday."""
        today = datetime.date.today()
        return (today.month == self._birthday.month and 
                today.day == self._birthday.day)

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        async_track_time_change(
            self.hass, self._handle_time_changed, hour=0, minute=0, second=0
        )
        self.update()
        
    @callback
    def _handle_time_changed(self, now):
        """Handle time changed."""
        self.schedule_update_ha_state(True)


class BirthdayCountdownSensor(SensorEntity):
    """Sensor for counting down days until birthday."""

    def __init__(self, child_config, entry_id=None):
        """Initialize the birthday countdown sensor."""
        self._name = child_config[CONF_NAME]
        try:
            self._birthday = datetime.datetime.strptime(
                child_config[CONF_BIRTHDAY], "%Y-%m-%d"
            ).date()
        except ValueError as e:
            _LOGGER.error(f"Invalid date format for {self._name}: {child_config[CONF_BIRTHDAY]}")
            raise e
        
        self._entry_id = entry_id
        self._state = None
        self._attributes = {}
        
        clean_name = self._name.lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        
        # HOME ASSISTANT STANDARD WAY
        self._attr_has_entity_name = True
        self._attr_name = "Birthday Countdown"
        self._attr_unique_id = f"birthday_countdown_{clean_name}"
        self._attr_native_unit_of_measurement = "days"
        self._attr_icon = ICON_BIRTHDAY
        
    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information."""
        if self._entry_id:
            clean_name = self._name.lower().replace(' ', '_')
            return DeviceInfo(
                identifiers={(DOMAIN, f"{self._entry_id}_{clean_name}")},
                name=self._name,  # Same device as allowance sensor
                manufacturer="Allowance Calculator",
                model="Child Tracker",
                sw_version="1.0.0",
            )
        return None
        
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
        
    def update(self):
        """Update the sensor."""
        try:
            today = datetime.date.today()
            age = calculate_age(self._birthday, today)
            days_until = self._days_until_birthday()
            next_birthday = self._get_next_birthday_date()
            
            self._state = days_until
            self._attributes = {
                "current_age": age,
                "birthday": self._birthday.strftime("%Y-%m-%d"),
                "next_birthday": next_birthday.strftime("%Y-%m-%d"),
                "is_birthday_today": days_until == 0,
                "birthday_weekday": next_birthday.strftime("%A"),
                "next_age": age + 1 if days_until == 0 else age + 1,
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating birthday countdown for {self._name}: {e}")
            
    def _days_until_birthday(self):
        """Calculate days until next birthday."""
        today = datetime.date.today()
        next_birthday = self._get_next_birthday_date()
        return (next_birthday - today).days
        
    def _get_next_birthday_date(self):
        """Get the next birthday date."""
        today = datetime.date.today()
        next_birthday = self._birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return next_birthday

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        async_track_time_change(
            self.hass, self._handle_time_changed, hour=0, minute=0, second=0
        )
        self.update()
        
    @callback
    def _handle_time_changed(self, now):
        """Handle time changed."""
        self.schedule_update_ha_state(True)