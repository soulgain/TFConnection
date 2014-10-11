#!/usr/bin/env python
#coding=utf-8

import mongoengine
import plistlib
from DBModel import TrainRecord
from DBModel import TrainConnectionRecord
import timeit
from config import config


mongoengine.connect(db='train', host=config['db_host'])
stations = plistlib.readPlist('./StationList.plist')['stations']


def main():
	for fromStation in stations:
		for toStation in stations:
			if fromStation['code'] == toStation['code']:
				continue

			if (TrainRecord.objects(__raw__={'fromStationCode':fromStation['code'], 'toStationCode':toStation['code']}).count()):
				print('direct: '+fromStation['code']+'->'+toStation['code'])
				continue

			print('connection analysing: '+fromStation['code']+'->'+toStation['code'])
			connection_between(fromStation['code'], toStation['code'])


def connection_between(fromStationCode, toStationCode):
	if (TrainRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode}).count()):
		print(getStationByCode(fromStationCode)+'->'+getStationByCode(toStationCode)+' no need to connect')
		return

	cursor1 = TrainRecord.objects(__raw__={'fromStationCode':fromStationCode})
	cursor2 = TrainRecord.objects(__raw__={'toStationCode':toStationCode})

	tcr = TrainConnectionRecord()
	tcr.fromStationCode = fromStationCode
	tcr.toStationCode = toStationCode

	for train1 in cursor1:
		for train2 in cursor2:
			if train1['toStationCode'] == train2['fromStationCode']:
				# print(getStationByCode(train1['fromStationCode'])+'->'+
				# 	getStationByCode(train1['toStationCode'])+'->'+
				# 	getStationByCode(train2['toStationCode']))

				has = False
				for path in tcr.paths:
					if path[0] == train1['toStationCode']:
						has = True
						break
				if not has:
					tcr.paths.append([train1['toStationCode']])

	if len(tcr.paths) > 0:	
		tcr.put()


def getStationByCode(stationCode):
	for station in stations:
		if station['code'] == stationCode:
			# print(station['name'].encode('utf-8'))
			return station['name'].encode('utf-8')


if __name__ == '__main__':
	# connection_between('AAX', 'BJP')
	# main()
	# getStationByCode('BJP')
	print(timeit.timeit('TrainRecord.objects(fromStationCode="SHH")', setup='from __main__ import TrainRecord', number=1000))
