#!/usr/bin/env python
#coding=utf-8

import flask
from flask import Flask
from flask import request
from flask import make_response
from flask_compress import Compress
from base64 import b64encode
from Crypto.Cipher import AES

import DBModel
import json
import mongoengine
from StationManager import StationManager
from config import config


app = Flask(__name__)
Compress().init_app(app)
app.config['COMPRESS_DEBUG'] = True
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

	if stationCodeOrName in stationCache:
		return stationCache[stationCodeOrName]


def make_json_response(object, encrypt=True):
	s = json.dumps(object, ensure_ascii=False, indent=2)

	if encrypt:
		key = config['cypher']
		paddingLen = 16-len(key)
		padding_map = ('\x00','\x01','\x02','\x03','\x04','\x05','\x06','\x07','\x08','\x09','\x0a','\x0b','\x0c','\x0d','\x0e','\x0f', '\x10')

		key = key + padding_map[paddingLen]*paddingLen

		def AESEncypt(key, dat):
			en = AES.new(key)
			out = en.encrypt(dat)
			return out

		padding = 16-len(s)%16
		if padding > 0:
			s += padding_map[padding] * padding
		s = b64encode(AESEncypt(key, s))

	resp = flask.Response(response=s, mimetype='application/json; charset=utf-8')
	# resp.headers['Content-Type'] = 'application/json'
	return resp


@app.route('/connection')
def connect():
	global stations

	fromStation = request.args.get('from', '')
	toStation = request.args.get('to', '')

	fromStation = findStationByCodeOrName(fromStation)
	toStation = findStationByCodeOrName(toStation)

	if not (fromStation and toStation):
		return make_json_response({'paths':[]})

	fromStationCode = fromStation['code']
	toStationCode = toStation['code']

	if 'mainStation' in fromStation:
		fromStationCode = fromStation['mainStation']

	if 'mainStation' in toStation:
		toStationCode = toStation['mainStation']

	connection_set = DBModel.TrainConnectionRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode})

	res = []
	if connection_set.count():
		connectionRecord = connection_set.first()
		paths = connectionRecord.paths

		for _, path in enumerate(paths):
			for index, connectStation in enumerate(path):
				if connectStation['distanceFactor'] > 1.5:
					continue

				station = findStationByCodeOrName(connectStation['connectStationCode'])
				desc = {'arrTrains': connectStation['arrTrains'],
						'depTrains': connectStation['depTrains'],
						'station': station['name'],
                        'stationCode': station['code'],
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

	return make_json_response({'paths':res})

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

	return make_json_response(tmp)


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
