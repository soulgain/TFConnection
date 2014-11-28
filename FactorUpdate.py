#!/usr/bin/env python
#coding=utf-8

from DBModel import TrainConnectionRecord
from StationManager import StationManager
import json


stationManager = StationManager()
stationManager.load()


def main():
	recordSet = TrainConnectionRecord.objects()

	for connection in recordSet:
		fromStation = stationManager.findStation(code=connection.fromStationCode)
		toStation = stationManager.findStation(code=connection.toStationCode)


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
