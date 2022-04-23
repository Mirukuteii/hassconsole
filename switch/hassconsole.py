"""Support for HassConsole component."""
import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.components import restart as hass_restart

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'hassconsole'

SW_TYPE = ['RestartHass']
SW_NAME = {'RestartHass': '重启Hass服务'}
SW_ICON = {'RestartHass': 'mdi:restart'}

def setup_platform(hass, config, add_devices, discovery_info=None):
    """加载【控制台-开关】"""
    devices = []
    devices.append(HassConsoleSW(hass, 'RestartHass', False))
    add_devices(devices)
    _LOGGER.debug("【控制台-开关】加载完成")

class HassConsoleSW(SwitchDevice):

    def __init__(self, hass, type, assumed=False):
        """Initialize the switch."""
        self.entity_id = 'switch'+'.'+type.lower()
        self.hass = hass
        self.type = type
        self._name = SW_NAME[type]
        self._icon = SW_ICON[type]
        self._assumed = assumed
        self._state = False
        self.attributes = None

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def assumed_state(self):
        """Return if the state is based on assumptions."""
        return self._assumed

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attributes

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.parse_type()
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._state = False
        self.schedule_update_ha_state()

    def parse_type(self):
        if self.type == 'RestartHass':
            self.hass.services.call('homeassistant', 'restart')
