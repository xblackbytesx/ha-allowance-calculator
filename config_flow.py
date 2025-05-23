"""Config flow for Allowance Calculator integration."""
import voluptuous as vol
import datetime
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_NAME, CONF_CURRENCY
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_CHILDREN,
    CONF_BIRTHDAY,
    CONF_PERCENTAGE,
    DEFAULT_PERCENTAGE,
    DEFAULT_CURRENCY,
    SUPPORTED_CURRENCIES,
)


class AllowanceCalculatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Allowance Calculator."""

    VERSION = 1
    
    def __init__(self):
        """Initialize the config flow."""
        self._data = {
            CONF_CHILDREN: [],
            CONF_CURRENCY: DEFAULT_CURRENCY,
        }

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            self._data[CONF_CURRENCY] = user_input[CONF_CURRENCY]
            return await self.async_step_add_child()
        
        # Show currency selection form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CURRENCY, default=DEFAULT_CURRENCY): 
                    vol.In(list(SUPPORTED_CURRENCIES.keys())),
            }),
            errors=errors,
        )

    async def async_step_add_child(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle adding a child."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate birthday format
                birthday = datetime.datetime.strptime(user_input[CONF_BIRTHDAY], "%Y-%m-%d").date()
                
                # Validate that birthday is in the past
                if birthday > datetime.datetime.now().date():
                    errors[CONF_BIRTHDAY] = "birthday_in_future"
                
                if not errors:
                    self._data[CONF_CHILDREN].append({
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_BIRTHDAY: user_input[CONF_BIRTHDAY],
                        CONF_PERCENTAGE: user_input.get(CONF_PERCENTAGE, DEFAULT_PERCENTAGE),
                    })
                    
                    # Ask if the user wants to add another child
                    return await self.async_step_add_another()
            except ValueError:
                errors[CONF_BIRTHDAY] = "invalid_date"
        
        # Show child form
        return self.async_show_form(
            step_id="add_child",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_BIRTHDAY): str,
                vol.Optional(CONF_PERCENTAGE, default=DEFAULT_PERCENTAGE): vol.Coerce(float),
            }),
            errors=errors,
            description_placeholders={
                "birthday_format": "YYYY-MM-DD",
            },
        )

    async def async_step_add_another(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Ask if the user wants to add another child."""
        if user_input is not None:
            if user_input.get("add_another", False):
                return await self.async_step_add_child()
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=f"Allowance Calculator ({len(self._data[CONF_CHILDREN])} children)",
                    data=self._data,
                )
        
        return self.async_show_form(
            step_id="add_another",
            data_schema=vol.Schema({
                vol.Required("add_another", default=False): bool,
            }),
            description_placeholders={
                "child_count": str(len(self._data[CONF_CHILDREN])),
                "children": ", ".join([child[CONF_NAME] for child in self._data[CONF_CHILDREN]]),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return AllowanceCalculatorOptionsFlow(config_entry)


class AllowanceCalculatorOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the Allowance Calculator."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_currency = self.config_entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_CURRENCY, default=current_currency): 
                    vol.In(list(SUPPORTED_CURRENCIES.keys())),
            }),
        )
