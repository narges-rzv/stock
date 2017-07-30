from os import listdir
import csv
from dateutil import parser
import numpy as np
import matplotlib.pylab as plt

datadic = {}

def load_data(dir1='../data/'):
	filenames = listdir(dir1)
	for fname in filenames:
		f = open(dir1+fname, 'r')
		datadic[fname]={}
		for l in f.readlines()[1:]:
			ws = l.strip().split(',')
			datadic[fname][parser.parse(ws[0])] = np.array([float(ws[1]),float(ws[2]),float(ws[3]),float(ws[4]),float(ws[5])])
	return datadic

def day_of_week(datadic):
	plot_data = {}
	for key1 in datadic:
		weekdayssum = np.zeros((7, len(datadic[key1])), dtype=float)
		for ix, d in enumerate(datadic[key1]):
			weekdayssum[d.weekday(), ix ] = datadic[key1][d][0]
		cnt = (weekdayssum != 0).sum(axis=1).ravel()
		weekdayssum[weekdayssum==0] = np.nan
		avgweekday = np.nanmean(weekdayssum, axis=1)
		stdweekday = np.nanstd(weekdayssum, axis=1)
		low = avgweekday - (1.96/np.sqrt(cnt)) * stdweekday
		high = avgweekday + (1.96/np.sqrt(cnt)) * stdweekday
		print('average opening for ', key1, ' is:', [('{0:4.3f}'.format(avgweekday[i]) + ' [' + '{0:4.3f}'.format(low[i]) + ' ' + '{0:4.3f}'.format(high[i]) + ']') for i in range(0,5)])
		plot_data[key1] = avgweekday, stdweekday
	return plot_data


