#!/usr/bin/env python
#coding=utf-8


from DBModel import TrainConnectionRecord
from DBModel import TrainRecord
import cPickle as pickle
import mongoengine
import time
import os
import sys
import plistlib
import json


mongoengine.connect(host='192.168.2.1', db='train')
stations = plistlib.readPlist('StationList.plist')['stations']


def statics_path_count():
	result = {}
	records = TrainConnectionRecord.objects
	total = TrainConnectionRecord.objects.count()

	print '\rstart...',

	current = 0
	for index, connection in enumerate(records):
		if current != str(int(float(index)/total*100)):
			current = str(int(float(index)/total*100))
			print(current)
			
		path_count = str(len(connection.paths))

		if path_count in result:
			result[path_count] = result[path_count]+1
		else:
			result[path_count] = 1

	with open('result', 'w') as file:
		pickle.dump(result, file)


def show_statics_path_count():
	with open('result', 'r') as file:
		result = pickle.load(file)

	print result


def statics_station_weight():
	result = {}

	for station in stations[:]:
		trainSet = TrainRecord.objects(fromStationCode=station['code'])

		tmp = {}
		for train in trainSet:
			if tmp.has_key(train.trainno):
				pass
			else:
				tmp[train.trainno] = 1

		result[station['name'].encode('utf-8')] = len(tmp.keys())

	with open('result', 'w') as file:
		json.dump(result, fp=file, ensure_ascii=False)


def show_statics_station_weight():
	result = None
	with open('result', 'r') as file:
		result = json.load(file)

	content = []
	for key in result:
		content.append(key+' '+str(result[key]))

	with open('tmp', 'w') as file:
		file.write('\n'.join(content).encode('utf-8'))


if __name__ == '__main__':
	# statics_path_count()
	# show_statics_path_count()
	# statics_station_weight()
	show_statics_station_weight()
