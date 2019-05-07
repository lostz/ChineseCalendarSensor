# -*- coding: utf-8 -*-

import logging
import json
import re
import configparser
import datetime

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, STATE_UNKNOWN, ATTR_DATE, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
PH = '''
[note]
name: china public holidyas
url: http://www.gov.cn/zhengce/index.htm
note: 为方便检查节假日命名和书写严格按照官网,!表示周末调为上班
[2019]
元旦: 1月1日
春节: 2月4日-10日, !2月2日, !2月3日
清明节: 4月5日
劳动节: 5月1日-4日, !4月28日, !5月5日
端午节: 6月7日
中秋节: 9月13日
国庆节: 10月1日-7日, !9月29日, !10月12日
[2018]
元旦: 1月1日
春节: 2月15日-21日, !2月11日, !2月24日
清明节: 4月5日-7日, !4月8日
劳动节: 4月29日-5月1日, !4月28日
端午节: 6月18日
中秋节: 9月24日
国庆节: 10月1日-7日, !9月29日, !9月30日
元旦2019: 12月30日-31日, !12月29日
[2017]
元旦: 1月1日, 1月2日
春节: 1月27日-2月2日, !1月2日, !2月4日
清明节: 4月2日-4日, !4月1日
劳动节: 5月1日
端午节: 5月28日-30日, !5月27日
中秋节、国庆节: 10月1日-8日, !9月30日
[2016]
元旦: 1月1日
春节: 2月7日-2月13日, !2月6日, !2月14日
清明节: 4月4日
劳动节: 5月1日, 5月2日
端午节: 6月9日-11日, !6月12日
中秋节: 9月15日-17日, !9月18日
国庆节: 10月1日-7日, !10月8日, !10月9日
[2015]
元旦: 1月1日-3日, !1月4日
春节: 2月18日-24日, !2月15日, !2月28日
清明节: 4月5日, 4月6日
劳动节: 5月1日
端午节: 6月20日, 6月22日
中秋节: 9月27日
国庆节: 10月1日-7日, !10月10日
中国人民抗日战争暨世界反法西斯战争胜利70周年纪念日: 9月3日-5日, !9月6日
[2014]
元旦: 1月1日
春节: 1月31日-2月6日, !1月26日, !2月8日
清明节: 4月5日, 4月7日
劳动节: 5月1日-3日, !5月4日
端午节: 6月2日
中秋节: 9月8日
国庆节: 10月1日-7日, !9月28日, !10月11日
[2013]
元旦: 1月1日-3日, !1月5日，!1月6日
春节: 2月9日-15日, !2月16日, !2月17日
清明节: 4月4日-6日, !4月7日
劳动节: 4月29日-5月1日, !4月27日, !4月28日
端午节: 6月10日-12日, !6月8日, !6月9日
中秋节: 9月19日-21日, !9月22日
国庆节: 10月1日-7日, !9月29日, !10月12日
[2012]
元旦: 1月1日-3日
春节: 1月22日-28日, !1月21日, !1月29日
清明节: 4月2日-4日, !3月31日, !4月1日
劳动节: 4月29日-5月1日, !4月28日
端午节: 6月22日-24日
中秋节、国庆节: 9月30日-10月7日, !9月29日
[2011]
元旦: 1月1日-3日
春节: 2月2日-8日, !1月30日, !2月12日
清明节: 4月3日-5日, !4月2日
劳动节: 4月30日-5月2日
端午节: 6月4日-6月6日
中秋节: 9月10日-12日
国庆节: 10月1日-7日, !10月8日, !10月9日
2012元旦: !12月31日
[2010]
元旦: 1月1日-3日
春节: 2月13日-19日, !2月20日, !2月21日
清明节: 4月3日-5日
劳动节: 5月1日-5月3日
端午节: 6月14日-16日, !6月12日, !6月13日
中秋节: 9月22日-24日, !9月19日, !9月25日
国庆节: 10月1日-7日, !9月26日, !10月9日
[2009]
元旦: 1月1日-3日, !1月4日
春节: 1月25日-31日, !1月24日, !2月1日
清明节: 4月4日-6日
劳动节: 5月1日-5月3日
端午节: 5月28日-30日, !5月31日
国庆节、中秋节: 10月1日-8日, !9月27日, !10月10日
[2008]
元旦: 1月1日
春节: 2月6日-12日, !2月2日, !2月3日
清明节: 4月4日-6日
五一国际劳动节: 5月1日-3日, !5月4日
端午节: 6月7日-9日
中秋节: 9月13日-15日
国庆节: 9月29日-10月5日, !9月27日, !9月28日
[2007]
元旦: 1月1日-3日
春节: 2月18日-24日, !2月17日, !2月25日
五一: 5月1日-7日, !4月28日, !4月29日
十一: 10月1日-7日, !9月29日, !9月30日
元旦2: !12月29日, 12月30日-31日
'''


_LOGGER = logging.getLogger(__name__)

DOMAIN = "chinese_calendar"

CONF_ATTRIBUTION = "中国节假日"

DEFAULT_NAME = 'Chinese Calendar'



def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    add_devices([ChineseCalendarSensor(name)], True)


class ChineseCalendarSensor(Entity):
    """Implementation of the Yahoo! weather sensor."""

    def __init__(self, name,days_path):
        """Initialize the sensor."""
        self._name = name
        self._state = STATE_UNKNOWN
        self._attr_name = ''
        self._date = ''
        self.public_holidays = []
        self.load_days_list()

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
        config = configparser.ConfigParser()
        config.read_string(PH.replace(" ", ""))
        for year in (y for y in config.sections() if y.isdigit()):
            for name, desc in config[year].items():
                for x in desc.split(','):
                    is_ph, p = self._parse_day(x)
                    start = datetime.date(int(year), p[0], p[1])
                    end = datetime.date(int(year), p[2], p[3])
                    self.public_holidays.extend(
                        [(start + datetime.timedelta(n), is_ph, name)
                         for n in range(int((end - start).days) + 1)])
    @staticmethod
    def _parse_day(string: str) -> list:
        '''
        转换
        "4月30日" -> True, [4, 30, 4, 30]
        "4月30日-31日" -> True, [4, 30, 4, 31]
        "4月30日-5月1日" -> True, [4, 30, 5, 1]
        "!4月30日" -> False, [4, 30, 4, 30]
        '''
        is_ph = not string.strip().startswith('!')
        m = re.match(r"(\d+月)(\d+日)-(\d+月)?(\d+日)", string.strip())
        if m:
            res = m.groups(default=m.groups()[0])
        else:
            m = re.search(r"(\d+)月(\d+)日", string)
            res = m.groups() * 2
        return is_ph, [int(x.replace("月", "").replace("日", "")) for x in res]

     def get_info(self, day):
        '''
        return: {
            is_public_holiday: 是否法定节假日,
            public_holiday_name: 法定节假日名字,
            is_holiday: 是否节假日,
            holiday_name: 节假日名字
        }
        '''
        res = {
        }
        for x in self.public_holidays:
            if x[0] == day:
                res["is_public_holiday"] = x[1]
                res["public_holiday_name"] = "工作日(" + \
                    x[2]+"调休)" if x[1] is False else x[2]
                res["is_holiday"] = res["is_public_holiday"]
                res["holiday_name"] = res["public_holiday_name"]
                break
        else:
            res["is_public_holiday"] = None
            res["public_holiday_name"] = "非法定节假日"
            res["is_holiday"] = day.weekday() >= 5
            res["holiday_name"] = "周末" if day.weekday() >= 5 else "工作日"
        return res

    def update(self):
        today=datetime.today().date().strftime('%Y-%m-%d')
        info = self.get_info(today)
        self._date = today
        if info["is_public_holiday"]:
            self._state = 'holiday'
            self.__attr_name = info["public_holiday_name"]
            return
        if info["is_holiday"]:
            self._state = "holiday"
            self._attr_name = info["holiday_name"]
            return
        self._state = "workday"
        self._attr_name = "工作日"

