#!/usr/bin/env python
# coding=utf-8

import requests
import json
import sys
import Queue
from threading import Thread as Thread
import cPickle as pickle
from StationManager import StationManager

BAIDU_AK = u'6d39dda6cfdf731a8e3e1c2c20c85648'
BAIDU_URL = u'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=%s'


class StationGeoFetcher(object):
    def __init__(self):
        pass

    @staticmethod
    def fetch(station):
        if isinstance(station, dict):
            station = station['name']

        r = None
        try:
            r = json.loads(requests.get(BAIDU_URL%(station+u'站', BAIDU_AK), timeout=20).content)
        except Exception as e:
            print(station+':\n'+repr(e))
            return

        if 'result' in r and 'location' in r['result']:
            return r['result']['location']

    @staticmethod
    def fetchFromList(stations):
        for station in stations:
            name = station['name']

            location = StationGeoFetcher.fetch(name)

            if location and 'lat' in location and 'lng' in location:
                station['location'] = location
            else:
                print(name)


def dispatch(stations, worker=4):
    queueList = []
    total = len(stations)
    part = total/(worker-1)

    for i in xrange(worker):
        tasks = []

        for j in xrange(i*part, (i+1)*part):
            if j < len(stations):
                tasks.append(stations[j])
            else:
                break

        queueList.append(tasks)

    threads = []
    for tasks in queueList:
        thread = Thread(target=StationGeoFetcher.fetchFromList, args=(tasks,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def print_locations(stations):
    for station in stations:
        if 'location' in station:
            print(station['name']+str(station['location']))
        else:
            print(station['name']+'no location data!')


if __name__ == '__main__':
    m = StationManager()
    m.load(use_gtgj=True)
    stations = m.stations
    # StationGeoFetcher.fetchFromList(stations)
    dispatch(stations, worker=20)
    # print_locations(stations)
    with open('stationWithGeo.pickle', 'w') as f:
        pickle.dump(stations, f)
