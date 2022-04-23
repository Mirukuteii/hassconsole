"""
Support for system infomation & control panel  in Home-assistant.
# Version: 0.01
# Author:  Mirukuteii
# Created: 2018-6-24
"""

import logging
# import mimetypes
# import os
import asyncio
from homeassistant.core import callback
from homeassistant.helpers.event import (
    async_track_point_in_utc_time, async_track_utc_time_change)

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (__version__, MAJOR_VERSION, MINOR_VERSION,
    PATCH_VERSION, CONF_NAME )

import homeassistant.config as config_util

from homeassistant.helpers.discovery import load_platform
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchDevice
# from homeassistant.components.camera import (Camera)
# from homeassistant.util import Throttle
import homeassistant.util.dt as dt_util
import requests
import re
import json
# import pytz
# import homeassistant.util.dt as dt_util
# import datetime
# from datetime import timedelta
# from math import (
#     sin, cos, tan, asin, acos, atan, atan2 ,
#     sqrt, floor, ceil, radians, degrees, pi)

_LOGGER = logging.getLogger(__name__)
DOMAIN = 'hassconsole'
DEFAULT_NAME = 'kzt'
ENTITY_ID_FORMAT = DOMAIN +'.{}'

# 实体字典
CONF_UPTIME = {'NAME': 'UPTIME', 'CNNAME': '运行时间', 'ICON': 'mdi:clock'}
CONF_VERSION = {'NAME': 'VERSION', 'CNNAME': '当前版本', 'ICON': 'mdi:clipboard-check'}
CONF_LATESTVER = {'NAME': 'LATESTVER', 'CNNAME': '最新版本', 'ICON': 'mdi:account-multiple'}
CONF_CONFIGPATH = {'NAME': 'CONFIGPATH', 'CNNAME': '配置文件根目录', 'ICON': 'mdi:file-multiple'}
CONF_CONFIGDICT = {'NAME': 'CONFIGDICT', 'CNNAME': '系统配置信息', 'ICON': 'mdi:dictionary'}

UPTIME_ATTR_1 = '开机时刻'
UPTIME_ATTR_2 = '总计秒数'
VERSION_ATTR_1 = '主版本号'
VERSION_ATTR_2 = '子版本号'
VERSION_ATTR_3 = '修正版本号'
LATESTVER_ATTR_1 = ''

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

@asyncio.coroutine
def async_setup(hass, config):
    """【控制台】开始加载"""
    name = config.get(CONF_NAME)
    # download_path = os.path.join(hass.config.path('downloads'))
    # if not os.path.isdir(download_path):
    #     _LOGGER.error("【控制台】下载路径: %s 不存在, 文件下载器无法启动.", download_path
    #     return False
    uptime   = Uptime(hass)
    version  = Version(hass)
    latestver  = LatestVer(hass)
    configpath = ConfigPath(hass)
    configdict = ConfigDict(hass)
    load_platform(hass, 'switch', DOMAIN, {}, config)
    # restart_hass = RestartHass(hass, True)
    _LOGGER.debug("【控制台】加载完成")
    return True

class Uptime(Entity):
    """显示Hass的运行时间."""

    def __init__(self, hass):
        """初始化实体, 最后调用回调函数更新实体."""
        self.hass = hass                   #必须
        self.initial = dt_util.now()
        self._name = CONF_UPTIME['CNNAME']
        self.entity_id = DOMAIN+'.'+CONF_UPTIME['NAME'].lower()
        self._state = None
        self.attributes = {}
        self._icon = CONF_UPTIME['ICON']
        self._unit = None
        async_track_utc_time_change(hass, self.timer_update, second=9)

    @property
    def state(self):
        """返回实体的状态值."""
        return self._state

    @property
    def state_attributes(self):
        """返回实体的状态属性值."""
        return self.attributes

    @property
    def name(self):
        """返回供前端显示的实体名(属性中的Friendly_name)."""
        return self._name

    @property
    def icon(self):
        """返回供前端显示的ICON图标."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回实体状态值的计量单位."""
        return self._unit

    @callback
    def update(self, now):
        """更新实体的所有属性.设为回调函数"""
        delta = dt_util.now() - self.initial
        delta = delta.total_seconds()
        self.attributes[UPTIME_ATTR_1] = str(self.initial)
        self.attributes[UPTIME_ATTR_2] = str(delta)
        self._unit = '秒'
        if delta > 60:
            self._unit = '分钟'
            delta /= 60
            if delta > 60:
                self._unit = '小时'
                delta /= 60
                if delta > 24:
                     self._unit = '天'
                     delta /= 24
        self._state = round(delta, 2)
        _LOGGER.debug("UPTIME更新: %s", delta)

    @callback
    def timer_update(self, time):
        """更新实体并在状态对象中刷新.设为回调函数"""
        self.update(time)
        self.async_schedule_update_ha_state()

class Version(Entity):
    """显示Hass的运行时间."""

    def __init__(self, hass):
        """初始化实体, 最后调用回调函数更新实体."""
        self.hass = hass                   #必须
        self.entity_id = DOMAIN+'.'+CONF_VERSION['NAME'].lower()
        self._name = CONF_VERSION['CNNAME']
        self._icon = CONF_VERSION['ICON']
        self._state = None
        self.attributes = {}
        self.timer_update()
        # async_track_utc_time_change(hass, self.timer_update, second=10)

    @property
    def state(self):
        """返回实体的状态值."""
        return self._state

    @property
    def state_attributes(self):
        """返回实体的状态属性值."""
        return self.attributes

    @property
    def name(self):
        """返回供前端显示的实体名(属性中的Friendly_name)."""
        return self._name

    @property
    def icon(self):
        """返回供前端显示的ICON图标."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回实体状态值的计量单位."""
        return None

    @callback
    def update(self, now):
        """更新实体的所有属性.设为回调函数"""
        self._state = __version__
        self.attributes[VERSION_ATTR_1] = MAJOR_VERSION
        self.attributes[VERSION_ATTR_2] = MINOR_VERSION
        self.attributes[VERSION_ATTR_3] = PATCH_VERSION

    @callback
    def timer_update(self, time=None):
        """更新实体并在状态对象中刷新.设为回调函数"""
        self.update(time)
        self.async_schedule_update_ha_state()

class LatestVer(Entity):
    """显示Hass的运行时间."""

    def __init__(self, hass):
        """初始化实体, 最后调用回调函数更新实体."""
        self.hass = hass                   #必须
        self.entity_id = DOMAIN+'.'+CONF_LATESTVER['NAME'].lower()
        self._name = CONF_LATESTVER['CNNAME']
        self._icon = CONF_LATESTVER['ICON']
        self._state = None
        self.attributes = {}
        self.timer_update()
        async_track_utc_time_change(hass, self.timer_update, hour=6, minute=6, second=6)

    @property
    def state(self):
        """返回实体的状态值."""
        return self._state

    @property
    def state_attributes(self):
        """返回实体的状态属性值."""
        return self.attributes

    @property
    def name(self):
        """返回供前端显示的实体名(属性中的Friendly_name)."""
        return self._name

    @property
    def icon(self):
        """返回供前端显示的ICON图标."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回实体状态值的计量单位."""
        return None

    # def get_hass_info(self, filepath):
    #     try:
    #         with open(filepath, 'r', encoding='utf-8') as file_data:
    #             hass_info = json.load(file_data)
    #     except (IndexError, FileNotFoundError, IsADirectoryError,
    #             UnboundLocalError):
    #         _Log.warning("File or data not present at the moment: %s",
    #                         os.path.basename(filepath))
    #         return
    #     return hass_info

    @callback
    def update(self, now):
        """更新实体的所有属性.设为回调函数"""
        # self.hass_info = get_hass_info(fp)


        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"}
        try:
            response =requests.get("https://pypi.python.org/pypi/homeassistant/json",headers=headers)
        except requests.exceptions.ConnectTimeout:
            _LOGGER.warning("【控制台】从pypi.python.org请求HA最新信息超时，尝试从官网爬取.")
        self.hass_info = response.json()
        self._state = self.hass_info['info']['version']

    @callback
    def timer_update(self, time=None):
        """更新实体并在状态对象中刷新.设为回调函数"""
        self.update(time)
        self.async_schedule_update_ha_state()

class ConfigPath(Entity):
    """显示Hass的配置文件根目录."""

    def __init__(self, hass):
        """初始化实体, 最后调用回调函数更新实体."""
        self.hass = hass                   #必须
        self.entity_id = DOMAIN+'.'+CONF_CONFIGPATH['NAME'].lower()
        self._name = CONF_CONFIGPATH['CNNAME']
        self._icon = CONF_CONFIGPATH['ICON']
        self._state = None
        self.attributes = {}
        self.timer_update()

    @property
    def state(self):
        """返回实体的状态值."""
        return self._state

    @property
    def state_attributes(self):
        """返回实体的状态属性值."""
        return self.attributes

    @property
    def name(self):
        """返回供前端显示的实体名(属性中的Friendly_name)."""
        return self._name

    @property
    def icon(self):
        """返回供前端显示的ICON图标."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回实体状态值的计量单位."""
        return None

    @callback
    def update(self, now):
        """更新实体的所有属性.设为回调函数"""
        self._state = config_util.get_default_config_dir()

    @callback
    def timer_update(self, time=None):
        """更新实体并在状态对象中刷新.设为回调函数"""
        self.update(time)
        self.async_schedule_update_ha_state()

class ConfigDict(Entity):
    """显示Hass的配置文件根目录."""

    def __init__(self, hass):
        """初始化实体, 最后调用回调函数更新实体."""
        self.hass = hass                   #必须
        self.entity_id = DOMAIN+'.'+CONF_CONFIGDICT['NAME'].lower()
        self._name = CONF_CONFIGDICT['CNNAME']
        self._icon = CONF_CONFIGDICT['ICON']
        self._state = None
        self.attributes = {}
        self.timer_update()

    @property
    def state(self):
        """返回实体的状态值."""
        return self._state

    @property
    def state_attributes(self):
        """返回实体的状态属性值."""
        return self.attributes

    @property
    def name(self):
        """返回供前端显示的实体名(属性中的Friendly_name)."""
        return self._name

    @property
    def icon(self):
        """返回供前端显示的ICON图标."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回实体状态值的计量单位."""
        return None

    @callback
    def update(self, now):
        """更新实体的所有属性.设为回调函数"""
        self._state = "详情见属性"
        self.attributes = self.hass.config.as_dict()

    @callback
    def timer_update(self, time=None):
        """更新实体并在状态对象中刷新.设为回调函数"""
        self.update(time)
        self.async_schedule_update_ha_state()
