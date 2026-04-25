"""Number platform for Marstek Venus E."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DOD_MIN, DOD_MAX
from .coordinator import MarstekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus E number entities."""
    coordinator: MarstekDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        MarstekDodNumber(coordinator, entry),
    ]
    
    async_add_entities(entities)


class MarstekDodNumber(CoordinatorEntity, NumberEntity):
    """Number entity for Marstek Venus E Depth of Discharge."""
    
    _attr_has_entity_name = True
    _attr_translation_key = "dod"

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Depth of Discharge"
        self._attr_unique_id = f"{entry.entry_id}_dod"
        self._attr_native_min_value = DOD_MIN
        self._attr_native_max_value = DOD_MAX
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:battery-arrow-down"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Marstek",
            "model": "Venus E",
        }
    
    @property
    def native_value(self) -> float | None:
        """Return the current DOD value."""
        # Get DOD from mode_data where it is reported by ES.GetMode
        if self.coordinator.mode_data and "dod" in self.coordinator.mode_data:
            try:
                return float(self.coordinator.mode_data["dod"])
            except (TypeError, ValueError):
                return None
        return None
    
    async def async_set_native_value(self, value: float) -> None:
        """Set a new DOD value."""
        try:
            dod_value = int(value)
            await self.coordinator.client.set_dod(dod_value)
            _LOGGER.info("DOD set to %d%%", dod_value)
            # Trigger a refresh to update the state in HA
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set DOD to %s: %s", value, err)
            raise