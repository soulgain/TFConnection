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
mongoengine.connect(host=config['db_host'], db='train')
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
			for index, connectStation in enumerate(path):
				station = findStationByCodeOrName(connectStation['connectStationCode'])
				desc = str(connectStation['arrTrains'])+'|'+station['name']+'|'+str(connectStation['depTrains'])
				path[index] = {"desc": desc}
				arrTrains = DBModel.TrainRecord.objects(fromStationCode=fromStationCode, toStationCode=station['code'])
				depTrains = DBModel.TrainRecord.objects(fromStationCode=station['code'], toStationCode=toStationCode)

				for arrTrain in arrTrains:
					for depTrain in depTrains:
						if arrTrain['trainno'] == depTrain['trainno']:
							path[index]['direct'] = True
							break
					if path[index].has_key('direct'):
						break

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
