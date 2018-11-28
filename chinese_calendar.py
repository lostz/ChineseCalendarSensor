# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, STATE_UNKNOWN, ATTR_DATE, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity


_LOGGER = logging.getLogger(__name__)

DOMAIN = "chinese_calendar"

CONF_ATTRIBUTION = "中国节假日"

DEFAULT_NAME = 'Chinese Calendar'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional('days_path','days_path'):cv.string
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    days_path = config.get('days_path')

    add_devices([ChineseCalendarSensor(name,days_path)], True)


class ChineseCalendarSensor(Entity):
    """Implementation of the Yahoo! weather sensor."""

    def __init__(self, name,days_path):
        """Initialize the sensor."""
        self._name = name
        self._state = STATE_UNKNOWN
        self._attr_name = ''
        self._date = ''
        self._days_path = days_path

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes.
        Implemented by component base class.
        """
        return {
            ATTR_DATE: datetime.today().date().strftime('%Y-%m-%d'),
            'name': self._attr_name
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }
    def load_days_list(self):
        with open(self._days_path, 'r') as f:
            data=json.load(f)
        days = {}
        days['holiday'] = {}
        days['workday'] =data['workday']
        for i in data['holiday']:
            start = datetime.strptime(i['start_time'],"%Y-%m-%d")
            end   = datetime.strptime(i['end_time'],"%Y-%m-%d")
            days['holiday'][i['name']] = {}
            days['holiday'][i['name']]['zh_name'] = i['zh_name']
            days['holiday'][i['name']]['days'] = []
            day = timedelta(days=1)
            for j in range((end-start).days+1):
                holiday = start +day *j
                days['holiday'][i['name']]['days'].append(holiday.strftime('%Y-%m-%d'))
        return days


    def update(self):
        today=datetime.today().date().strftime('%Y-%m-%d')
        if self._date ==today:
            return
        self._date = today
        days = self.load_days_list()
        if today in days['workday']:
            self._state = 'workday'
            return
        for i in days['holiday']:
            if today in days['holiday'][i]['days']:
                self._state = 'holiday'
                self._attr_name = i['zh_name']
        weekday = datetime.today().weekday()
        if weekday<=1:
            self._state = 'holiday'
            self._attr_name = '周末'
        else:
            self._state = 'workday'

