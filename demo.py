#!/usr/bin/env python
#coding=utf-8

from flask import Flask
from flask import request

import DBModel
import json
import mongoengine
from StationManager import StationManager
from config import config


app = Flask(__name__)
mongoengine.connect(host=config['db_host'], db='train')
stationManager = StationManager()
stationManager.load('stationWithGeo.pickle')
stations = stationManager.stations
stationCache = {}

for _,station in enumerate(stations):
	stationCode = station['code']
	stationName = station['name']
	stationCache[stationCode] = station
	stationCache[stationName] = station


def findStationByCodeOrName(stationCodeOrName):
	global stationCache
	return stationCache[stationCodeOrName]


@app.route('/connection')
def connect():
	global stations

	fromStation = request.args.get('from', '')
	toStation = request.args.get('to', '')

	fromStation = findStationByCodeOrName(fromStation)
	toStation = findStationByCodeOrName(toStation)

	fromStationCode = fromStation['code']
	toStationCode = toStation['code']

	if 'mainStation' in fromStation:
		fromStationCode = fromStation['mainStation']

	if 'mainStation' in toStation:
		toStationCode = toStation['mainStation']

	connection_set = DBModel.TrainConnectionRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode})

	if connection_set.count() == 0:
		return ''
	else:
		connectionRecord = connection_set.first()
		paths = connectionRecord.paths
		res = []

		for _, path in enumerate(paths):
			for index, connectStation in enumerate(path):
				if connectStation['distanceFactor'] > 1.5:
					continue

				station = findStationByCodeOrName(connectStation['connectStationCode'])
				desc = {'arrTrains': connectStation['arrTrains'],
						'depTrains': connectStation['depTrains'],
						'station': station['name'],
						'distanceFactor': connectStation['distanceFactor']}
				res.append(desc)
				# desc = '|'.join([str(connectStation['arrTrains']), station['name'], str(connectStation['depTrains']), str(connectStation['distanceFactor'])[:4]])
				# path[index] = {"desc": desc}

		def cmp(p1, p2):
			if (p1['arrTrains']+p1['depTrains']) - (p2['arrTrains']+p2['depTrains'])> 0:
				return -1
			else:
				return 1

		res.sort(cmp=cmp)

		return '<pre>'+json.dumps({'paths':res}, ensure_ascii=False, indent=2)+'</pre>'

@app.route('/connectionByCount')
def connectionByCount():
	count = request.args.get('count', None)
	skip = request.args.get('skip', 0)
	limit = request.args.get('limit', 10)

	skip = int(skip)
	limit = int(limit)

	if not count:
		return

	connection_set = DBModel.TrainConnectionRecord.objects(paths__size=20).skip(skip).limit(limit)

	tmp = json.loads(connection_set.to_json())
	
	for connectionRecord in tmp:
		connectionRecord['fromStationName'] = findStationByCodeOrName(connectionRecord['fromStationCode'])['name']
		connectionRecord['toStationName'] = findStationByCodeOrName(connectionRecord['toStationCode'])['name']
		paths = connectionRecord['paths']

		for _, path in enumerate(paths):
			for index, stationCode in enumerate(path):
				station = findStationByCodeOrName(stationCode)
				path[index] = station['name']

	return '<pre>'+json.dumps(tmp, indent=2, ensure_ascii=False)+'</pre>'


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
