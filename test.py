#!/usr/bin/env python
#coding=utf-8

import mongoengine
from DBModel import TrainRecord


mongoengine.connect(db='train', host='192.168.2.1')

cursor1 = TrainRecord.objects(__raw__={'fromStationCode':'SHH'})
cursor2 = TrainRecord.objects(__raw__={'toStationCode':'BJP'})





