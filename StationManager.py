#!/usr/bin/env python
#coding=utf8


import plistlib
import cPickle as pickle
import xml.etree.ElementTree as xml


class StationManager(object):
    def __init__(self):
        self.stations = []
        self._stationCache = {}
        self._mainStationCache = {}

    def _buildCache(self):
        if not len(self.stations):
            return

        self._stationCache = {}
        for station in self.stations:
            self._stationCache[station['code']] = station
            self._stationCache[station['name']] = station

        for station in self.stations:
            if not 'mainStationCode' in station:
                continue

            mainStationCode = station['mainStationCode']

            if not mainStationCode in self._mainStationCache:
                self._mainStationCache[mainStationCode] = []

            nearStations = self._mainStationCache[mainStationCode]
            if not station['code'] in nearStations:
                nearStations.append(station['code'])

    def _importFromPickle(self, fpath='stationList.pickle'):
        with open(fpath, 'r') as fp:
            stations = pickle.load(fp)
            self.stations = stations
        self._buildCache()

    def _importStationlistFromPlist(self, fpath = 'StationList.plist'):
        self.stations = plistlib.readPlist(fpath)['stations']
        self._buildCache()

    def _importFromGTGJ(self, fpath='gtgj_stations.xml'):
        tree = None

        with open(fpath, 'r') as fp:
            tree = xml.parse(fp)

        poplist = tree.getroot().find('bd').find('poplist')
        stationlist = tree.getroot().find('bd').find('stationlist')
        tmp = {}

        for station in poplist.findall('s'):
            station_dict = {}
            station_dict['code'] = station.find('c').text
            station_dict['firstLetter'] = station.find('jp').text
            station_dict['hotIndex'] = 1
            station_dict['isPopStation'] = True
            station_dict['name'] = station.find('n').text
            station_dict['pinyin'] = station.find('py').text
            station_dict['mainStationCode'] = station.find('o').text

            tmp[station_dict['code']] = station_dict

        for station in stationlist.findall('s'):
            station_dict = {}
            station_dict['code'] = station.find('c').text
            station_dict['firstLetter'] = station.find('jp').text
            station_dict['hotIndex'] = -1
            station_dict['isPopStation'] = False
            station_dict['name'] = station.find('n').text
            station_dict['pinyin'] = station.find('py').text
            station_dict['mainStationCode'] = station.find('o').text

            tmp[station_dict['code']] = station_dict

        self.stations = tmp.values()
        self._buildCache()

    def findStation(self, code=None, name=None):
        if code:
            if code in self._stationCache:
                return self._stationCache[code]
            else:
                for station in self.stations:
                    if station['code'] == code:
                        self._stationCache[code] = station
                        return  station

        if name:
            if name in self._stationCache:
                return  self._stationCache[name]
            else:
                for station in self.stations:
                    if station['name'] == name:
                        self._stationCache[name] = station
                        return station

    def findNearStations(self, mainStationCode=None):
        if not mainStationCode in self._mainStationCache:
            return []

        return self._mainStationCache[mainStationCode]


    """
        -------------|------------
        |code        |AAX
        |firstLetter |aax
        |hotIndex    |-1
        |isPopStation|False
        |name        |昂昂溪
        |pinyin      |angangxi
        |simpleCode  |
        |------------|------------
        |mainStation |Station(BJP)
        |nearStations|[Station(BJP), Station(XXX)]
        -------------|------------
    """
    def generate(self):
        for station in self.stations:
            name = station['name']

            if len(name) > 2 and name[-1] in (u'东', u'南', u'西', u'北'):
                location_name = station['name'][:-1]
                mainStation = self.findStation(name=location_name)

                if mainStation:
                    station['mainStationCode'] = mainStation['code']

        self.dump()


    def dump(self, fpath='stationList.pickle'):
        if len(self.stations):
            with open(fpath, 'w') as fp:
                pickle.dump(self.stations, fp)

    def load(self, fpath=None, use_plist=False, use_gtgj=False):
        if use_plist:
            self._importStationlistFromPlist(fpath or 'StationList.plist')
        elif use_gtgj:
            self._importFromGTGJ(fpath or 'gtgj_stations.xml')
        else:
            self._importFromPickle(fpath or 'stationWithGeo.pickle')


if __name__ == '__main__':
    m = StationManager()
    m.load()
    print('there are '+str(len(m.stations))+' stations')
    # m.generate()
    mainstation_list = []

    for station in m.stations:
        if 'mainStationCode' in station:
            mainstation_list.append(station)

    print('there are '+ str(len(mainstation_list)) +' main-stations')
    print([m.findStation(code=code)['pinyin'] for code in m.findNearStations('CDW')])
