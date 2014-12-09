#!/usr/bin/env python
#coding=utf-8

import mongoengine
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


class TrainRecord(mongoengine.DynamicDocument):
	trainno = mongoengine.StringField(required = True)
	trainid = mongoengine.StringField(required = True)
	fromStationCode = mongoengine.StringField(required = True)
	toStationCode = mongoengine.StringField(required = True)
	meta = {
		'collection': 'TrainRecord',
		'index_background': True,
		'indexes': [
            ('trainno', 'fromStationCode', 'toStationCode'),
			('trainno',),
        ]
	}
	_inner_record = None

	'''
		parse from a trainDTO json struct
	'''
	def parse(self, trainDTO):
		self.trainno = trainDTO['station_train_code']
		self.trainid = trainDTO['train_no']
		self.fromStationCode = trainDTO['from_station_telecode']
		self.toStationCode = trainDTO['to_station_telecode']
		rset = TrainRecord.objects(trainno=self.trainno, fromStationCode=self.fromStationCode, toStationCode=self.toStationCode)
		if rset.count():
			self._inner_record = rset.first()

		if self._inner_record:
			self._inner_record.fromStationName = trainDTO['from_station_name']
			self._inner_record.toStationName = trainDTO['to_station_name']
			# addition
			self._inner_record.startStationCode = trainDTO['start_station_telecode']
			self._inner_record.startStationName = trainDTO['start_station_name']
			self._inner_record.endStationCode = trainDTO['end_station_telecode']
			self._inner_record.endStationName = trainDTO['end_station_name']
			self._inner_record.startTime = trainDTO['start_time']
			self._inner_record.arriveTime = trainDTO['arrive_time']
			self._inner_record.dayDifference = trainDTO['day_difference']
			self._inner_record.trainClassName = trainDTO['train_class_name']
			self._inner_record.durationTime = trainDTO['lishi']
			self._inner_record.durationMinutes = trainDTO['lishiValue']
			self._inner_record.seatTypes = trainDTO['seat_types']
			self._inner_record.fromStationNo = trainDTO['from_station_no']
			self._inner_record.toStationNo = trainDTO['to_station_no']
			self._inner_record.saleTime = trainDTO['sale_time']
		else:
			# supply
			self.fromStationName = trainDTO['from_station_name']
			self.toStationName = trainDTO['to_station_name']
			# addition
			self.startStationCode = trainDTO['start_station_telecode']
			self.startStationName = trainDTO['start_station_name']
			self.endStationCode = trainDTO['end_station_telecode']
			self.endStationName = trainDTO['end_station_name']
			self.startTime = trainDTO['start_time']
			self.arriveTime = trainDTO['arrive_time']
			self.dayDifference = trainDTO['day_difference']
			self.trainClassName = trainDTO['train_class_name']
			self.durationTime = trainDTO['lishi']
			self.durationMinutes = trainDTO['lishiValue']
			self.seatTypes = trainDTO['seat_types']
			self.fromStationNo = trainDTO['from_station_no']
			self.toStationNo = trainDTO['to_station_no']
			self.saleTime = trainDTO['sale_time']

	def put(self):
		if self._inner_record:
			self._inner_record.save()
		else:
			self.save()

	def __repr__(self):
		return self.fromStationCode+'->'+self.toStationCode+' '+self.trainno


class TrainConnectionRecord(mongoengine.Document):
	fromStationCode = mongoengine.StringField(required = True)
	toStationCode = mongoengine.StringField(required = True)
	paths = mongoengine.ListField(required = True)
	meta = {
		'collection': 'TrainConnectionRecord',
		'index_background': True,
		'indexes': [
            ('fromStationCode', 'toStationCode')
        ]
	}


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


class TrainStopRecord(mongoengine.Document):
	trainNo = mongoengine.StringField(required=True)
	trainId = mongoengine.StringField(required=True)
	stops = mongoengine.ListField(required=True)
	meta = {
		'collection': 'TrainStopRecord',
		'index_background': True,
		'indexes': [
			('trainNo',),
            ('trainId',)
        ]
	}

	def put(self):
		rset = TrainStopRecord.objects(trainNo=self.trainNo)

		if rset.count() > 0:
			r = rset.first()
			r.trainId = self.trainId
			r.stops = self.stops
			r.save()

			for i in xrange(1, rset.count()):
				rset[i].delete()
		else:
			self.save()


if __name__ == '__main__':
	pass
