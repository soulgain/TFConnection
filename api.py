#!/usr/bin/env python
#coding=utf-8

import requests
import datetime


'''
	API for query train info
'''
class TrainQuery(object):
	'''
		Initializer for TrainQuery class
	'''
	def __init__(self, fromStationCode, toStationCode, date = None):
		self.fromStationCode = fromStationCode
		self.toStationCode = toStationCode

		if date == None:
			self.date = (datetime.date.today()+datetime.timedelta(days=15)).isoformat()
		else:
			self.date = date

	'''
		Do the query according the params
	'''
	def query(self):
		if not(self.fromStationCode and self.toStationCode):
			return
			
		# https://kyfw.12306.cn/otn/lcxxcx/query
		# https://kyfw.12306.cn/otn/leftTicket/query
		queryStr = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={date}&from_station={fromStationCode}&to_station={toStationCode}'.format(date=self.date, fromStationCode=self.fromStationCode, toStationCode=self.toStationCode)

		try:
			headers = {'Accept-Encoding': 'gzip,deflate,sdch'}
			print(queryStr)
			r = requests.get(queryStr, verify=False, headers=headers, timeout=30)
			r = r.json()['data']['datas']

			return r
		except Exception as e:
			pass


'''
	API for query train stops info
'''
class TrainStopQuery(object):
	def __init__(self, trainid, fromStationCode, toStationCode, date=None):
		self.trainid = trainid
		self.fromStationCode = fromStationCode
		self.toStationCode = toStationCode
		if date == None:
			self.date = (datetime.date.today()+datetime.timedelta(days=15)).isoformat()
		else:
			self.date = date

	def query(self):
		url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=%s' % (self.trainid, self.fromStationCode, self.toStationCode, self.date)

		try:
			headers = {'Accept-Encoding': 'gzip,deflate,sdch'}
			print(url)
			r = requests.get(url, verify=False, headers=headers, timeout=30)
			r = r.json()['data']['data']

			return r
		except Exception as e:
			pass


if __name__ == '__main__':
	r = TrainQuery(fromStationCode='BJP', toStationCode='SHH', date=(datetime.date.today()+datetime.timedelta(days=3)).isoformat()).query()
	print(r)

	r = TrainStopQuery(fromStationCode='SYT', toStationCode='JMB', trainid='15000020950E').query()
	print(r)
