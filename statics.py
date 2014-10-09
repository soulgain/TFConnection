#!/usr/bin/env python
#coding=utf-8


from DBModel import TrainConnectionRecord
import cPickle as pickle
import mongoengine
import time
import os
import sys


mongoengine.connect(host='192.168.2.1', db='train')


def view_bar(num=1, sum=100, bar_word=":"):   
	rate = float(num) / float(sum)   
	rate_num = int(rate * 100)   
	print '%d%% :' %(rate_num),  

	for i in range(0, num):   
		os.write(1, bar_word)   
		sys.stdout.flush() 


def statics_path_count():
	result = {}
	records = TrainConnectionRecord.objects
	total = TrainConnectionRecord.objects.count()

	print '\rstart...',

	current = 0
	for index, connection in enumerate(records):
		if current != str(int(float(index)/total*100)):
			current = str(int(float(index)/total*100))
			print(current)
			
		path_count = str(len(connection.paths))

		if path_count in result:
			result[path_count] = result[path_count]+1
		else:
			result[path_count] = 1

	with open('result', 'w') as file:
		pickle.dump(result, file)


if __name__ == '__main__':
	statics_path_count()
