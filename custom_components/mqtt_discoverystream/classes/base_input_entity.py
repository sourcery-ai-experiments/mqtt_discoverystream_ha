"""Base for all discovery entities with input alternatives."""

import logging

from homeassistant.components import mqtt
from homeassistant.components.button.const import SERVICE_PRESS
from homeassistant.components.number import (
    ATTR_MAX,
    ATTR_MIN,
    ATTR_STEP,
    ATTR_VALUE,
    SERVICE_SET_VALUE,
)
from homeassistant.components.select import ATTR_OPTION, ATTR_OPTIONS
from homeassistant.components.text import ATTR_PATTERN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_STATE,
    SERVICE_SELECT_OPTION,
    STATE_UNKNOWN,
)

from ..const import (
    ATTR_MODE,
    ATTR_PRESS,
    ATTR_SET,
    CONF_CMD_T,
    CONF_MAX,
    CONF_MIN,
    CONF_MODE,
    CONF_OPS,
    CONF_PATTERN,
    CONF_STAT_T,
    CONF_STEP,
)
from ..utils import EntityInfo, validate_message
from .base_entity import DiscoveryEntity

_LOGGER = logging.getLogger(__name__)


class ButtonDiscoveryEntity(DiscoveryEntity):
    """Button class."""

    def __init__(
        self,
        hass,
        publish_retain,
        platform,
    ):
        """Initialise the button class."""
        super().__init__(
            hass,
            publish_retain,
            platform,
            publish_state=False,
        )

    def build_config(self, config, entity_info: EntityInfo):
        """Build the config for a button."""
        del config[CONF_STAT_T]
        config[CONF_CMD_T] = f"{entity_info.mycommand}{ATTR_PRESS}"

    async def _async_handle_message(self, msg):
        """Handle a message for a button."""
        valid, domain, entity, command = validate_message(  # pylint: disable=unused-variable
            self._hass, msg, self._platform
        )
        if not valid:
            return

        service_payload = {
            ATTR_ENTITY_ID: f"{domain}.{entity}",
        }
        await self._hass.services.async_call(domain, SERVICE_PRESS, service_payload)


class NumberDiscoveryEntity(DiscoveryEntity):
    """Number class."""

    def build_config(self, config, entity_info: EntityInfo):
        """Build the config for a number."""
        config[CONF_CMD_T] = f"{entity_info.mycommand}{ATTR_SET}"
        config[CONF_MAX] = entity_info.attributes[ATTR_MAX]
        config[CONF_MIN] = entity_info.attributes[ATTR_MIN]
        config[CONF_MODE] = entity_info.attributes[ATTR_MODE]
        config[CONF_STEP] = entity_info.attributes[ATTR_STEP]

    async def _async_handle_message(self, msg):
        """Handle a message for a number."""
        valid, domain, entity, command = validate_message(  # pylint: disable=unused-variable
            self._hass, msg, self._platform
        )
        if not valid:
            return

        service_payload = {
            ATTR_ENTITY_ID: f"{domain}.{entity}",
            ATTR_VALUE: msg.payload,
        }
        await self._hass.services.async_call(domain, SERVICE_SET_VALUE, service_payload)


class SelectDiscoveryEntity(DiscoveryEntity):
    """Select class."""

    def build_config(self, config, entity_info: EntityInfo):
        """Build the config for a select."""
        if ATTR_OPTIONS in entity_info.attributes:
            config[CONF_OPS] = entity_info.attributes[ATTR_OPTIONS]
        config[CONF_CMD_T] = f"{entity_info.mycommand}{ATTR_SET}"

    async def _async_handle_message(self, msg):
        """Handle a message for a select."""
        valid, domain, entity, command = validate_message(  # pylint: disable=unused-variable
            self._hass, msg, self._platform
        )
        if not valid:
            return

        service_payload = {
            ATTR_ENTITY_ID: f"{domain}.{entity}",
            ATTR_OPTION: msg.payload,
        }
        await self._hass.services.async_call(
            domain, SERVICE_SELECT_OPTION, service_payload
        )


class TextDiscoveryEntity(DiscoveryEntity):
    """Text class."""

    def __init__(
        self,
        hass,
        publish_retain,
        platform,
    ):
        """Initialise the text class."""
        super().__init__(
            hass,
            publish_retain,
            platform,
            publish_state=False,
        )

    def build_config(self, config, entity_info: EntityInfo):
        """Build the config for a text."""
        config[CONF_CMD_T] = f"{entity_info.mycommand}{ATTR_SET}"
        config[CONF_MAX] = entity_info.attributes[ATTR_MAX]
        config[CONF_MIN] = entity_info.attributes[ATTR_MIN]
        config[CONF_MODE] = entity_info.attributes[ATTR_MODE]
        if entity_info.attributes[ATTR_PATTERN]:
            config[CONF_PATTERN] = entity_info.attributes[ATTR_PATTERN]

    async def async_publish_state(self, new_state, mybase):
        """Publish the state for a text."""

        if new_state.state != STATE_UNKNOWN:
            await mqtt.async_publish(
                self._hass,
                f"{mybase}{ATTR_STATE}",
                new_state.state,
                1,
                self._publish_retain,
            )

        await super().async_publish_state(new_state, mybase)

    async def _async_handle_message(self, msg):
        """Handle a message for a text."""
        valid, domain, entity, command = validate_message(  # pylint: disable=unused-variable
            self._hass, msg, self._platform
        )
        if not valid:
            return

        service_payload = {
            ATTR_ENTITY_ID: f"{domain}.{entity}",
            ATTR_VALUE: msg.payload,
        }
        await self._hass.services.async_call(domain, SERVICE_SET_VALUE, service_payload)
