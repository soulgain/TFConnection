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


mongoengine.connect('train', host='192.168.2.1')

stations = plistlib.readPlist('./StationList.plist')['stations'][:]
cache_code_to_index = {}
row_and_colum = len(stations)
table = []
# table += '0'*row_and_colum*row_and_colum

for index, value in enumerate(stations):
	cache_code_to_index[value['code']] = index


def table_get(row, col):
	global table

	return table[row*row_and_colum+col]


def table_set(row, col, value):
	global table

	table[row*row_and_colum+col] = value


def table_get_row(row):
	global table

	return [table[index] for index in xrange(row*row_and_colum, row*row_and_colum+row_and_colum)]


def table_get_col(col):
	global table

	return [table[index] for index in xrange(col, col+row_and_colum*row_and_colum, row_and_colum)]


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
		if listFrom[x] == '1' and listTo[x] == '1':
			res.append(stations[x]['code'])

	return res


def table_dump():
	global table

	with open('./table', 'w') as file:
		pickle.dump(table, file)


def table_load():
	global table

	if os.path.isfile('./table'):
		print('loading from file...')
		with open('./table', 'r') as file:
			try:
				table = pickle.load(file)
			except Exception, e:
				print(e)

	print('table load from file: '+str(len(table)))


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


if __name__ == '__main__':
	# init_table()
	# table_dump()
	table_load()

	# timeit.timeit("connection_between('AAX', 'BJP')", number=100, setup="from __main__ import connection_between")

	# print connection_between('AAX', 'BJP')
	main()
