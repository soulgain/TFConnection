#!/usr/bin/env python
#coding=utf-8

import threading
import mongoengine
import Queue
import plistlib
from api import TrainQuery
from DBModel import TrainRecord


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
				trainDTOs = TrainQuery(fromStationCode, toStationCode).query()

				if not trainDTOs:
					continue

				for trainDTO in trainDTOs:
					tr = TrainRecord()
					tr.parse(trainDTO)
					tr.put()

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
		

def readStationList():
	bundle = plistlib.readPlist('./StationList.plist')
	stations = bundle['stations']

	return stations[:count]


if __name__ == '__main__':
	mongoengine.connect('train')

	# according to the network condition
	# worker_num maybe more
	manager = Manager(worker_num=20)

	stations = readStationList()

	for fromStation in stations[:]:
		for toStation in stations:
			if fromStation == toStation:
				continue
			manager.tasks.put((fromStation['code'], toStation['code']))

	manager.dispatch()
