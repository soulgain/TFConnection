#!/usr/bin/env python
#coding=utf-8

import pymongo
import mongoengine
from DBModel import TrainRecord
from DBModel import TrainConnectionRecord
import timeit
import plistlib
import cPickle as pickle
import os
import sys
import threading
import Queue
from table import Table


mongoengine.connect('train', host='192.168.2.1')

stations = plistlib.readPlist('./StationList.plist')['stations'][:]
cache_code_to_index = {}
row_and_colum = len(stations)
table = Table(row_and_colum, row_and_colum)


for index, value in enumerate(stations):
	cache_code_to_index[value['code']] = index


def init_table():
	for index, station in enumerate(stations):
		set = TrainRecord.objects(fromStationCode=station['code'])

		for train in set:
			toStationCode = train['toStationCode']
			if toStationCode in cache_code_to_index:
				table_set(index, cache_code_to_index[toStationCode], '1')


def connection_between(fromStationCode, toStationCode):
	global cache_code_to_index

	fromIndex = cache_code_to_index[fromStationCode]
	toIndex = cache_code_to_index[toStationCode]

	if table_get(fromIndex, toIndex) == '1':
		return

	listFrom = table_get_row(fromIndex)
	listTo = table_get_col(toIndex)

	res = []

	for x in xrange(row_and_colum):
		if listFrom[x] != None and listTo[x] != None:
			res.append(stations[x]['code'])

	return res


def table_dump():
	global table

	with open('./table', 'w') as file:
		table.dump(file)


def table_load():
	global table

	if os.path.isfile('./table'):
		print('Loading from file...')
		with open('./table', 'r') as file:
			try:
				table.load(file)
			except Exception, e:
				print(e)


def main():
	for fromStation in stations[445:]:
		for toStation in stations:
			if fromStation['code'] == toStation['code']:
				continue

			print('connection analysing: '+fromStation['code']+'->'+toStation['code'])
			r = connection_between(fromStation['code'], toStation['code'])

			if r == None or len(r) == 0:
				print('direct: '+fromStation['code']+'->'+toStation['code'])
			else:
				paths = [[path] for path in r]
				tcr = TrainConnectionRecord()
				tcr.fromStationCode = fromStation['code']
				tcr.toStationCode = toStation['code']
				tcr.paths = paths
				tcr.put()


class Analyser(threading.Thread):
	def __init__(self, taskQueue):
		threading.Thread.__init__(self)
		self.taskQueue = taskQueue

	def run(self):
		while True:
			try:
				fromStationCode, toStationCode = self.taskQueue.get(False)
				print('connection analysing: '+fromStationCode+'->'+toStationCode+' remain: '+str(self.taskQueue.qsize()))

				r = connection_between(fromStationCode, toStationCode)

				if r == None or len(r) == 0:
					print('direct: '+fromStationCode+'->'+toStationCode)
				else:
					paths = [[path] for path in r]
					tcr = TrainConnectionRecord()
					tcr.fromStationCode = fromStationCode
					tcr.toStationCode = toStationCode
					tcr.paths = paths
					tcr.put()
			except Queue.Empty as e:
				print(e)
				break
			else:
				continue


class Manager(object):
	def __init__(self, worker_num=1):
		self.worker_num = worker_num;
		self.tasks = Queue.Queue()

	def dispatch(self):
		threads = []

		for x in xrange(0, self.worker_num):
			analyser = Analyser(self.tasks)
			analyser.start()
			threads.append(analyser)

		for analyser in threads:
			analyser.join()


if __name__ == '__main__':
	# init_table()
	# table_dump()
	table_load()

	# timeit.timeit("connection_between('AAX', 'BJP')", number=100, setup="from __main__ import connection_between")

	# print connection_between('AAX', 'BJP')
	# main()
	manager = Manager(worker_num=10)

	for fromStation in stations[:]:
		for toStation in stations:
			if fromStation['code'] != toStation['code']:
				task = (fromStation['code'], toStation['code'])
				manager.tasks.put(task)
			else:
				continue

	manager.dispatch()
