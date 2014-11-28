#!/usr/bin/env python
#coding=utf-8

from DBModel import TrainConnectionRecord
from StationManager import StationManager
import json
from distanceCalc import calcu_distance


stationManager = StationManager()
stationManager.load()


def distance_between(station1, station2):
	return calcu_distance(station1['location'], station2['location'])


def main():
	recordSet = TrainConnectionRecord.objects()

	for connection in recordSet:
		fromStation = stationManager.findStation(code=connection.fromStationCode)
		toStation = stationManager.findStation(code=connection.toStationCode)
		dis = distance_between(fromStation, toStation)

		for path in connection.paths:
			connectionStation = stationManager.findStation(code=path.connectStationCode)
			dis2 = distance_between(fromStation, connectionStation)+distance_between(connectionStation, toStation)
			factor = float(dis2)/dis
			path.distanceFactor = factor

		connection.save()


def mergeGEOData():
	wgi_stations = None
	stations = None

	with open('wgi_stations.json', 'r') as file:
		wgi_stations = json.load(file)

	cache_dict = {}

	for station in wgi_stations['data']:
		cache_dict[station['code']] = station

	with open('stationWithGeo.json', 'r') as file:
		stations = json.load(file)

	for station in stations:
		cached_station = cache_dict[station['code']]

		if cache_dict:
			location = {'lat':cached_station['wgs84_lat'], 'lng':cached_station['wgs84_long']}
			if 'location' in station:
				print(station['location'], ' -> ', location)
			station['location'] = location
		else:
			print(statoin, 'not found!')

	with open('stationWithGeo.json', 'w') as file:
		json.dump(stations, file)

if __name__ == '__main__':
	mergeGEOData()
	# main()
