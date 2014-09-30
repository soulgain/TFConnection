#!/usr/bin/env python
#coding=utf-8

import cPickle as pickle


class Table(object):
	'''
		a table structure.
	'''
	def __init__(self, rows, cols, value=None):
		super(Table, self).__init__()
		self.backend_list = [value for _ in xrange(rows*cols)]
		self.rows = rows
		self.cols = cols

	'''
		get the value of table at (row, col).
	'''
	def get(self, row, col):
		return self.backend_list[row*self.rows + col]

	'''
		get the value to table at (row, col).
	'''
	def set(self, row, col, value):
		self.backend_list[row*self.rows+col] = value

	'''
		return a list as the row of table.
	'''
	def get_row(self, row):
		return [self.backend_list[index] for index in xrange(row*self.cols, row*self.cols+self.cols)]

	'''
		return a list as the col of table.
	'''
	def get_col(self, col):
		return [self.backend_list[index] for index in xrange(col, col+self.rows*self.cols, self.cols)]

	'''
		dump table to file.
	'''
	def dump(self, file):
		table = {}
		table['rows'] = self.rows
		table['cols'] = self.cols
		table['backend'] = self.backend_list

		pickle.dump(table, file)

	'''
		load table from a file.
	'''
	def load(self, file):
		table = pickle.load(file)
		self.backend_list = table['backend']
		self.rows = table['rows']
		self.cols = table['cols']


def test():
	t = Table(5, 5, 0)
	t.set(2, 0, 10)
	t.set(3, 3, 20)
	print t.get_row(0)
	print t.get_row(1)
	print t.get_row(2)
	print t.get_row(3)
	print t.get_row(4)

	return t


if __name__ == '__main__':
	t = test()
	with open('test', 'w') as file:
		t.dump(file)

		