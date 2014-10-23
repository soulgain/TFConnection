#!/usr/bin/env python
#coding=utf-8

import mongoengine
import requests
import api
import plistlib


class Path(object):
	"""
		arrTrains: 到达中转站可选车次数量
		depTrains: 从中转站出发可选车次数量
		connectStationCode: 中转站点code
		distanceFactor:
	"""
	def __init__(self, arrTrains=None, depTrains=None, connectStationCode=None, distanceFactor=0.0):
		self.arrTrains = arrTrains
		self.depTrains = depTrains
		self.connectStationCode = connectStationCode
		self.distanceFactor = distanceFactor

	def toDict(self):
		return {'connectStationCode': self.connectStationCode,
				'arrTrains': self.arrTrains,
				'depTrains': self.depTrains,
                'distanceFactor': self.distanceFactor}

	def __eq__(self, other):
		if self.connectStationCode != other.connectStationCode:
			return False

		if self.arrTrains != other.arrTrains:
			return False

		if self.depTrains != other.depTrains:
			return False

		return True

	def __ne__(self, other):
		return not self.__eq__(self, other)

	def __repr__(self):
		return str(self.arrTrains)+'|'+self.connectStationCode+'|'+str(self.depTrains)


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
	meta = {'collection': 'TrainConnectionRecordTemp'}


	def put(self):
		recordSet = TrainConnectionRecord.objects(fromStationCode=self.fromStationCode, toStationCode=self.toStationCode)

		if recordSet.count() > 0:
			record = recordSet.first()

			record.paths = self.paths
			record.save()

			# delete other record
			if recordSet.count() > 1:
				for record in recordSet[1:]:
					record.delete()
		else:
			self.save()

	def __repr__(self):
		return self.fromStationCode+'->'+self.toStationCode+'\n'+str(self.paths)


if __name__ == '__main__':
	pass
