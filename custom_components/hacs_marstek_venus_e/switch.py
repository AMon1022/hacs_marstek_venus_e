"""Switch platform for Marstek Venus E."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarstekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus E switch entities.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        async_add_entities: Callback to add entities
    """
    coordinator: MarstekDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        MarstekLedSwitch(coordinator, entry),
    ]
    
    async_add_entities(entities)


class MarstekLedSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for Marstek Venus E LED control."""
    
    _attr_has_entity_name = True
    _attr_translation_key = "led_ctrl"

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch.
        
        Args:
            coordinator: Data update coordinator
            entry: Configuration entry
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_led_ctrl"
        self._attr_icon = "mdi:led-on"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Marstek",
            "model": "Venus E",
        }
    
    @property
    def is_on(self) -> bool | None:
        """Return True if LED is on."""
        # Try to find LED state in available data sources
        for source in [self.coordinator.data, self.coordinator.mode_data]:
            if source and "led_ctrl" in source:
                return bool(source["led_ctrl"])
        return None
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the LED on."""
        try:
            await self.coordinator.client.set_led_ctrl(True)
            _LOGGER.info("LED turned on")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on LED: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the LED off."""
        try:
            await self.coordinator.client.set_led_ctrl(False)
            _LOGGER.info("LED turned off")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off LED: %s", err)
            raise