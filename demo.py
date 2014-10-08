#!/usr/bin/env python
#coding=utf-8

from flask import Flask
from flask import request

import DBModel
import json
import mongoengine

app = Flask(__name__)
mongoengine.connect(db='train')


@app.route('/connection')
def connect():
	fromStationCode = request.args.get('from', '')
	toStationCode = request.args.get('to', '')
	connection_set = DBModel.TrainConnectionRecord.objects(__raw__={'fromStationCode':fromStationCode, 'toStationCode':toStationCode})

	if connection_set.count() == 0:
		return ''
	else:
		connectionRecord = connection_set.first()
		paths = connectionRecord.paths
		return json.dumps({'paths':paths})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
