#!/usr/bin/env python
#coding=utf-8

from flask import Flask
from flask import request

import DBModel
import json
import mongoengine
import plistlib
from config import config


app = Flask(__name__)
mongoengine.connect(host=config['host'], db='train')
stations = plistlib.readPlist('StationList.plist')['stations']
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

	fromStationCode = findStationByCodeOrName(fromStation)['code']
	toStationCode = findStationByCodeOrName(toStation)['code']

	connection_set = DBModel.TrainConnectionRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode})

	if connection_set.count() == 0:
		return ''
	else:
		connectionRecord = connection_set.first()
		paths = connectionRecord.paths

		for _, path in enumerate(paths):
			for index, stationCode in enumerate(path):
				station = findStationByCodeOrName(stationCode)
				path[index] = station['name']

		return '<pre>'+json.dumps({'paths':paths}, ensure_ascii=False, indent=2)+'</pre>'

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
