#!/usr/bin/env python
# coding=utf-8

import requests
import json
import sys


BAIDU_AK = '6d39dda6cfdf731a8e3e1c2c20c85648'
BAIDU_URL = 'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=%s'


class StationGeoFetcher(object):
    def __init__(self):
        pass

    @staticmethod
    def fetch(station):
        if isinstance(station, dict):
            station = station['name']

        r = None
        try:
            r = json.loads(requests.get(BAIDU_URL%(station+'站', BAIDU_AK), timeout=10).content)
        except Exception as e:
            print(station+':\n'+repr(e))

        if 'result' in r and 'location' in r['result']:
            return r['result']['location']


if __name__ == '__main__':
    print StationGeoFetcher.fetch('大灰厂')
