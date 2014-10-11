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

	def __repr__(self):
		return self.fromStationCode+'->'+self.toStationCode+' '+self.trainno


'''
	read stations from a plist file
'''
def readFromPlist():
	bundle = plistlib.readPlist('StationList.plist')
	stations = bundle['stations']

	return stations


class TrainConnectionRecord(mongoengine.Document):
	fromStationCode = mongoengine.StringField(required = True)
	toStationCode = mongoengine.StringField(required = True)
	paths = mongoengine.ListField(required = True)

	'''
		compare two path
		actually there are two lists of string
	'''
	@staticmethod
	def comparePath(path1, path2):
		if len(path1) != len(path2):
			return False

		for x in xrange(0, len(path1)):
			if path1[x] != path2[x]:
				return False

		return True


	def put(self):
		recordSet = TrainConnectionRecord.objects(fromStationCode=self.fromStationCode, toStationCode=self.toStationCode)

		if recordSet.count() > 0:
			record = recordSet.first()

			record.paths = self.paths
			record.save()
		else:
			self.save()

	def __repr__(self):
		return self.fromStationCode+'->'+self.toStationCode+'\n'+str(self.paths)


if __name__ == '__main__':
	pass
