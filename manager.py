#!/usr/bin/env python
#coding=utf-8

import threading
import mongoengine
import Queue
import plistlib
from api import TrainQuery
from api import TrainStopQuery
from DBModel import TrainRecord
from DBModel import TrainStopRecord
from StationManager import StationManager
import datetime


class Worker(threading.Thread):
	def __init__(self, taskQueue):
		threading.Thread.__init__(self)
		self.taskQueue = taskQueue

	def run(self):
		while True:
			try:
				fromStationCode, toStationCode = self.taskQueue.get(False)
				# print(fromStationCode+'-'+toStationCode
				# continue
				date = (datetime.date.today()+datetime.timedelta(days=15)).isoformat()
				trainDTOs = TrainQuery(fromStationCode, toStationCode, date=date).query()

				if not trainDTOs:
					continue

				for trainDTO in trainDTOs:
					tr = TrainRecord()
					tr.parse(trainDTO)
					tr.put()

					try:
						rset = TrainStopRecord.objects(trainId=tr.trainid)
						if rset.count() == 0:
							r = TrainStopQuery(fromStationCode=fromStationCode,
										   toStationCode=toStationCode,
										   trainid=tr.trainid,
										   date=date).query()

							if not r or len(r)==0:
								continue

							tsr = TrainStopRecord()
							tsr.trainId = tr.trainid
							tsr.trainNo = tr.trainno
							tsr.stops = r
							tsr.put()
					except Exception as e:
						print(e)

			except Queue.Empty:
				break
			else:
				continue


class Manager(object):
	def __init__(self, worker_num=1):
		self.worker_num = worker_num;
		self.tasks = Queue.Queue()

	def dispatch(self):
		threads = []

		for x in xrange(1, self.worker_num):
			worker = Worker(self.tasks)
			worker.start()
			threads.append(worker)

		for worker in threads:
			worker.join()


if __name__ == '__main__':
	mongoengine.connect('train')

	# according to the network condition
	# worker_num maybe more
	manager = Manager(worker_num=20)

	stationManager = StationManager()
	stationManager.load()
	stations = stationManager.stations

	for fromStation in stations[:]:
		for toStation in stations:
			if fromStation == toStation:
				continue
			manager.tasks.put((fromStation['code'], toStation['code']))

	manager.dispatch()
