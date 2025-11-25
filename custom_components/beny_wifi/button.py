"""Button entities for Beny Wifi."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MODEL, SERIAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_id = config_entry.data[SERIAL]
    device_model = config_entry.data[MODEL]

    buttons = [
        BenyWifiSendMaxCurrentButton(
            coordinator,
            "send_max_current",
            device_id=device_id,
            device_model=device_model,
        )
    ]

    async_add_entities(buttons)


class BenyWifiSendMaxCurrentButton(ButtonEntity):
    """Button to send max current value to the charger."""

    def __init__(self, coordinator, key, device_id=None, device_model=None):
        """Initialize the button entity."""
        self.coordinator = coordinator
        self.key = key
        self._attr_translation_key = key
        self._device_id = device_id
        self._device_model = device_model
        self.entity_id = f"button.{device_id}_{key}"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:send"

    @property
    def unique_id(self):
        """Return a unique ID for this button entity."""
        return f"{self._device_id}_{self.key}"

    async def async_press(self) -> None:
        """Handle the button press - send current max_current value to device."""
        # Get the current value from the number entity
        number_entity_id = f"number.{self._device_id}_max_current_control"
        number_state = self.hass.states.get(number_entity_id)
        
        if number_state is None:
            _LOGGER.error(
                f"Could not find number entity {number_entity_id} to read max current value"
            )
            return
        
        try:
            max_current = int(float(number_state.state))
            
            # Validate range
            if not (6 <= max_current <= 32):
                _LOGGER.error(
                    f"Max current value {max_current}A is out of range (6-32A)"
                )
                return
            
            # Send to device using coordinator
            device_name = f"Beny Charger {self._device_id}"
            await self.coordinator.async_set_max_current(device_name, max_current)
            
            _LOGGER.info(
                f"Successfully sent max current {max_current}A to {device_name}"
            )
            
        except (ValueError, TypeError) as e:
            _LOGGER.error(
                f"Error converting max current value: {number_state.state}, error: {e}"
            )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"Beny Charger {self._device_id}",
            manufacturer="ZJ Beny",
            model=self._device_model,
            serial_number=self._device_id,
        )