#!/usr/bin/env python
#coding=utf-8


import math

def rad(flo):
    return flo * math.pi / 180.0

def calcu_distance(location1, location2):
    lat1 = float(location1['lat'])
    lng1 = float(location1['lng'])

    lat2 = float(location2['lat'])
    lng2 = float(location2['lng'])

    earth_radius=6378.137
    radlat1=rad(lat1)
    radlat2=rad(lat2)
    a=radlat1-radlat2
    b=rad(lng1)-rad(lng2)
    s=2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(radlat1)*math.cos(radlat2)*math.pow(math.sin(b/2),2)))
    s=s*earth_radius
    if s<0:
        return round(-s,2)
    else:
        return round(s,2)


if __name__ == '__main__':
    print calcu_distance({'lat':30.59411, 'lng':104.0638}, {'lat':30.6047, 'lng':104.0667})
