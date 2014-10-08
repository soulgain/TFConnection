#!/usr/bin/env python
#coding=utf-8

from flask import Flask
from flask import request

import DBModel
import json
import mongoengine
import plistlib


app = Flask(__name__)
mongoengine.connect(db='train')
stations = plistlib.readPlist('StationList.plist')['stations']
stationCache = {}

for _,station in enumerate(stations):
	stationCode = station['code']
	stationCache[stationCode] = station


def findStationByCode(stationCode):
	global stationCache
	return stationCache[stationCode]


@app.route('/connection')
def connect():
	global stations

	fromStationCode = request.args.get('from', '')
	toStationCode = request.args.get('to', '')
	connection_set = DBModel.TrainConnectionRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode})

	if connection_set.count() == 0:
		return ''
	else:
		connectionRecord = connection_set.first()
		paths = connectionRecord.paths

		for _, path in enumerate(paths):
			for index, stationCode in enumerate(path):
				station = findStationByCode(stationCode)
				path[index] = station['name']

		return json.dumps({'paths':paths}, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
