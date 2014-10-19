#!/usr/bin/env python
#coding=utf-8

import pymongo
import mongoengine
from DBModel import TrainRecord
from DBModel import TrainConnectionRecord
from DBModel import Path
import timeit
import plistlib
import cPickle as pickle
import os
import sys
import threading
import Queue
from table import Table
from config import config
from StationManager import StationManager


mongoengine.connect('train', host=config['db_host'])

stationManager = StationManager()
stationManager.load()

stations = []
for station in stationManager.stations:
    if not 'mainStationCode' in station:
        stations.append(station)

cache_code_to_index = {}
row_and_colum = len(stations)
table = Table(row_and_colum, row_and_colum)


for index, value in enumerate(stations):
    cache_code_to_index[value['code']] = index


def init_table():
    global table
    global stationManager

    for index, station in enumerate(stations):
        set = [tr for tr in TrainRecord.objects(fromStationCode=station['code'])]

        nearStations = stationManager.findNearStations(station['code'])

        if len(nearStations):
            for nearStationCode in nearStations:
                set += [tr for tr in TrainRecord.objects(fromStationCode=nearStationCode)]

        tmp = {}

        for train in set:
            toStationCode = train['toStationCode']
            toStation = stationManager.findStation(code=toStationCode)

            if toStation and 'mainStationCode' in toStation:
                toStationCode = toStation['mainStationCode']

            if not toStationCode in tmp:
                tmp[toStationCode] = {}

            tmp[toStationCode][train['trainno']] = 1

        for toStationCode in tmp:
            if toStationCode in cache_code_to_index:
                table.set(index, cache_code_to_index[toStationCode], tmp[toStationCode].keys())


def connection_between(fromStationCode, toStationCode):
    global cache_code_to_index
    global table

    fromIndex = cache_code_to_index[fromStationCode]
    toIndex = cache_code_to_index[toStationCode]

    # check if there is a direct line
    # if table.get(fromIndex, toIndex):
    # 	return

    listFrom = table.get_row(fromIndex)
    listTo = table.get_col(toIndex)

    res = []

    for x in xrange(row_and_colum):
        arr = listFrom[x]
        dep = listTo[x]

        if arr and dep:
            if len(arr) == 1 and len(dep) == 1:
                # 避免K123 -> K123 这样的转车
                if arr[0] != dep[0]:
                    path = Path(arrTrains=len(arr), depTrains=len(dep), connectStationCode=stations[x]['code'])
                    res.append(path)
            else:
                path = Path(arrTrains=len(arr), depTrains=len(dep), connectStationCode=stations[x]['code'])
                res.append(path)

    return res


def table_dump():
    global table

    with open('table', 'w') as file:
        table.dump(file)


def table_load():
    global table

    if os.path.isfile('table'):
        print('Loading from file...')
        with open('table', 'r') as file:
            try:
                table.load(file)
            except Exception, e:
                print(e)


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
                    pass
                    # print('direct: '+fromStationCode+'->'+toStationCode)
                else:
                    paths = [[path.toDict()] for path in r]
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
    init_table()
    # table_dump()
    # table_load()
    sys.exit(0)

    # timeit.timeit("connection_between('AAX', 'BJP')", number=100, setup="from __main__ import connection_between")

    # print connection_between('AAX', 'BJP')
    manager = Manager(worker_num=30)

    for fromStation in stations[:10]:
        for toStation in stations:
            if fromStation['code'] != toStation['code']:
                task = (fromStation['code'], toStation['code'])
                manager.tasks.put(task)
            else:
                continue

    manager.dispatch()
