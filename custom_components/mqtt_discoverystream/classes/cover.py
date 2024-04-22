"""cover methods for MQTT Discovery Statestream."""

import logging

from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
    ATTR_CURRENT_TILT_POSITION,
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntityFeature,
)
from homeassistant.components.mqtt.cover import (
    CONF_GET_POSITION_TEMPLATE,
    CONF_GET_POSITION_TOPIC,
    CONF_TILT_STATUS_TEMPLATE,
    CONF_TILT_STATUS_TOPIC,
    DEFAULT_PAYLOAD_CLOSE,
    DEFAULT_PAYLOAD_OPEN,
    DEFAULT_PAYLOAD_STOP,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_SUPPORTED_FEATURES,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    SERVICE_SET_COVER_POSITION,
    SERVICE_SET_COVER_TILT_POSITION,
    SERVICE_STOP_COVER,
    Platform,
)

from ..const import (
    ATTR_ATTRIBUTES,
    ATTR_SET,
    ATTR_SET_POSITION,
    ATTR_SET_TILT,
    CONF_CMD_T,
    CONF_SET_POS_T,
    CONF_TILT_CMD_T,
)
from ..utils import EntityInfo, command_error, validate_message
from .entity import DiscoveryEntity

_LOGGER = logging.getLogger(__name__)


class DiscoveryItem(DiscoveryEntity):
    """Cover class."""

    PLATFORM = Platform.COVER

    def build_config(self, config, entity_info: EntityInfo):
        """Build the config for a cover."""
        config[CONF_CMD_T] = f"{entity_info.mycommand}{ATTR_SET}"

        if ATTR_CURRENT_POSITION in entity_info.attributes:
            config[CONF_GET_POSITION_TOPIC] = f"{entity_info.mybase}{ATTR_ATTRIBUTES}"
            config[CONF_GET_POSITION_TEMPLATE] = (
                "{{ value_json['" + ATTR_CURRENT_POSITION + "'] }}"
            )

        if (
            entity_info.attributes[ATTR_SUPPORTED_FEATURES]
            & CoverEntityFeature.SET_POSITION
        ):
            config[CONF_SET_POS_T] = f"{entity_info.mycommand}{ATTR_SET_POSITION}"

        if (
            entity_info.attributes[ATTR_SUPPORTED_FEATURES]
            & CoverEntityFeature.SET_TILT_POSITION
        ):
            config[CONF_TILT_CMD_T] = f"{entity_info.mycommand}{ATTR_SET_TILT}"

        if ATTR_CURRENT_TILT_POSITION in entity_info.attributes:
            config[CONF_TILT_STATUS_TOPIC] = f"{entity_info.mybase}{ATTR_ATTRIBUTES}"
            config[CONF_TILT_STATUS_TEMPLATE] = (
                "{{ value_json['" + ATTR_CURRENT_TILT_POSITION + "'] }}"
            )

    async def _async_handle_message(self, msg):
        """Handle a message for a cover."""
        valid, domain, entity, command = validate_message(
            self._hass, msg, DiscoveryItem.PLATFORM
        )
        if not valid:
            return

        service_payload = {
            ATTR_ENTITY_ID: f"{domain}.{entity}",
        }
        if command == ATTR_SET:
            if msg.payload == DEFAULT_PAYLOAD_OPEN:
                await self._hass.services.async_call(
                    domain, SERVICE_OPEN_COVER, service_payload
                )
            elif msg.payload == DEFAULT_PAYLOAD_CLOSE:
                await self._hass.services.async_call(
                    domain, SERVICE_CLOSE_COVER, service_payload
                )
            elif msg.payload == DEFAULT_PAYLOAD_STOP:
                await self._hass.services.async_call(
                    domain, SERVICE_STOP_COVER, service_payload
                )
            else:
                command_error(command, msg.payload, entity)
        elif command == ATTR_SET_POSITION:
            service_payload[ATTR_POSITION] = msg.payload
            await self._hass.services.async_call(
                domain, SERVICE_SET_COVER_POSITION, service_payload
            )
        elif command == ATTR_SET_TILT:
            service_payload[ATTR_TILT_POSITION] = msg.payload
            await self._hass.services.async_call(
                domain, SERVICE_SET_COVER_TILT_POSITION, service_payload
            )
