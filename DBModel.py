#!/usr/bin/env python
#coding=utf-8

import mongoengine
import requests
import api
import plistlib


class TrainRecord(mongoengine.Document):
	trainno = mongoengine.StringField(required = True)
	trainid = mongoengine.StringField(required = True)
	fromStationCode = mongoengine.StringField(required = True)
	toStationCode = mongoengine.StringField(required = True)

	'''
		parse from a trainDTO json struct
	'''
	def parse(self, trainDTO):
		self.trainno = trainDTO['station_train_code']
		self.trainid = trainDTO['train_no']
		self.fromStationCode = trainDTO['from_station_telecode']
		self.toStationCode = trainDTO['to_station_telecode']

	def put(self):
		recordSet = TrainRecord.objects(trainno=self.trainno, fromStationCode=self.fromStationCode, toStationCode=self.toStationCode)

		if not recordSet.count():
			self.save()


'''
	read stations from a plist file
'''
def readFromPlist():
	bundle = plistlib.readPlist('./StationList.plist')
	stations = bundle['stations']

	return stations[:30]


if __name__ == '__main__':
	mongoengine.connect('train')
	
	stations = readFromPlist()

	for fromStation in stations:
		for toStation in stations:
			if fromStation == toStation:
				continue

			try:
				ret = api.TrainQuery(fromStationCode=fromStation['code'], toStationCode=toStation['code']).query().json()['data']

				if len(ret) > 0:
					for trainDTO in ret:
						trainDTO = trainDTO['queryLeftNewDTO']
						record = TrainRecord()
						record.parse(trainDTO)
						record.put()
			except Exception as e:
				print(e)
