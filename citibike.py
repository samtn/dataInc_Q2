#!/usr/bin/python

import sys
import csv
import numpy as np
from math import radians, cos, sin, asin, sqrt

#----------------------------------------------------------------
def calc_circle_dist(lon1, lat1, lon2, lat2):
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	return km

#----------------------------------------------------------------
filename = sys.argv[1]

data=[]
with open(filename, 'rb') as fh:
	reader = csv.reader(fh)
	for row in reader:
		if row[0] != "tripduration":
			data.append(row)

trip_dur =[]
start_end_same = 0
month_tripdur = {}
dist_traveled = []
bike_to_station = {}
overtime = 0
station_to_hours = {}
bike_to_moved ={}
hours_to_count = {}
for i in range(24):
	hours_to_count[i] = 0

for i in range(1,13):
	month_tripdur[i] = []

for row in data:
	# What is the median trip duration, in seconds?
	trip_dur.append(int(row[0]))

	# What fraction of rides start and end at the same station?
	if int(row[3]) ==  int(row[7]):
		start_end_same += 1

	# Calculate the average duration of trips for each month in the year.
	month = int(row[1].split('/')[0])
	month_tripdur[month].append(int(row[0]))

	# What is the standard deviation of the number of stations visited by a bike?
	bikeid = int(row[11])
	if bikeid not in bike_to_station:
		bike_to_station[bikeid] = set()
	bike_to_station[bikeid].add(int(row[3]))
	bike_to_station[bikeid].add(int(row[7]))


	# What is the average length, in kilometers, of a trip?
	try:
		dist_traveled.append(calc_circle_dist(float(row[6]), float(row[5]), float(row[10]), float(row[9])))
	except ValueError:
		pass


	# What fraction of rides exceed their corresponding time limit?
	if row[12] == "Subscriber" and int(row[0]) > 45*60:
		overtime += 1
	elif row[12] == "Customer" and int(row[0]) > 30*60:
		overtime += 1

	# What is the largest ratio of station hourly usage fraction to system hourly usage fraction 
	station_id = int(row[3])
	hour = int(row[1].split()[1].split(":")[0])
	if station_id not in station_to_hours:
		station_to_hours[station_id] = {}
		station_to_hours[station_id]['total'] = 0
	if hour not in station_to_hours[station_id]:
		station_to_hours[station_id][hour] = 0
	station_to_hours[station_id][hour] += 1.0	
	station_to_hours[station_id]['total'] += 1.0
	hours_to_count[hour] += 1.0

	# What is the average number of times a bike is moved 
	if bikeid not in bike_to_moved:
		bike_to_moved[bikeid] = [int(row[7]), 0]
	else:
		if int(row[3]) != bike_to_moved[bikeid][0]:
			bike_to_moved[bikeid][1] += 1.0
		bike_to_moved[bikeid][0] = int(row[7])	



trip_dur = np.array(trip_dur)
print "1. Median trip duration:\t%s" %np.median(trip_dur)

print "5. Fraction of same start-end stations:\t%s" %(start_end_same / float(len(data)))

month_ave = []
for month in month_tripdur:
	month_ave.append(np.mean(month_tripdur[month]))
print "3. Difference between month durations (max-min):\t%s" %(max(month_ave)-min(month_ave))

print "6. Average traveled distance in km:\t%s" %(np.mean(dist_traveled))

station_visit = []
for bikeid in bike_to_station:
	station_visit.append(len(bike_to_station[bikeid]))
print "2. Mean and SD of number of stations visited by a bike:\t%s\t%s" %(np.mean(station_visit), np.std(station_visit))

print "4. Fraction of people exceeded their time:\t%s" %(overtime/float(len(data)))


# normalize per station
ratios=[]
for station_id in station_to_hours:
	for hour in station_to_hours[station_id]:
		if hour != 'total':
			station_to_hours[station_id][hour] /= station_to_hours[station_id]['total'] 
			station_to_hours[station_id][hour] /= (hours_to_count[hour] / len(data))
			ratios.append(station_to_hours[station_id][hour])
print "7. Maximum ratio of hourly usage:\t%s" %(max(ratios))

moved = []
for bikeid in bike_to_moved:
	if bike_to_moved[bikeid][1] > 0:
		moved.append(bike_to_moved[bikeid][1])
moved =  np.array(moved)
print "8. Average number of times a bike is moved:\t%s" %(np.mean(moved))







