from os import listdir
import csv
from dateutil import parser
import numpy as np
import matplotlib.pylab as plt
from urllib.request import Request, urlopen

import urllib

'''Doesn't work yet :( '''
def download_historical_data(stname='amzn', dir1='../data/'):
    stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/'+stname+'?period1=1343620800&period2=1501387200&interval=1d&events=history&crumb=xBC5oaavHyP'
    print(stock_url)
    fname=dir1+stname+'.csv'
    response = urlopen(stock_url)

def load_data(dir1='../data/', datefrom='', dateto=''):
    datadic = {}
    filenames = listdir(dir1)
    for fname in filenames:
        f = open(dir1+fname, 'r')
        datadic[fname]={}
        for l in f.readlines()[1:]:
            ws = l.strip().split(',')
            date1 = parser.parse(ws[0]) 
            if datefrom != '' and dateto != '':
                if (date1 > parser.parse(datefrom)) and (date1 < parser.parse(dateto)) : 
                    datadic[fname][date1] = np.array([float(ws[1]),float(ws[2]),float(ws[3]),float(ws[4]),float(ws[5])])
    return datadic

def day_of_week(datadic):
    plot_data = {}
    for key1 in datadic:
        weekdayssum = np.zeros((7, len(datadic[key1])), dtype=float)
        for ix, d in enumerate(datadic[key1]):
            weekdayssum[d.weekday(), ix ] = datadic[key1][d][3]
        cnt = (weekdayssum != 0).sum(axis=1).ravel()
        weekdayssum[weekdayssum==0] = np.nan
        avgweekday = np.nanmean(weekdayssum, axis=1)
        stdweekday = np.nanstd(weekdayssum, axis=1)
        low = avgweekday - (1.96/np.sqrt(cnt)) * stdweekday
        high = avgweekday + (1.96/np.sqrt(cnt)) * stdweekday
        print('average opening for ', key1, ' is:', [('{0:4.3f}'.format(avgweekday[i]) + ' [' + '{0:4.3f}'.format(low[i]) + ' ' + '{0:4.3f}'.format(high[i]) + ']') for i in range(0,5)])
        plot_data[key1] = avgweekday, stdweekday
    labels = ['mon','tue','wed','thu','fri','sat','sun']
    return plot_data, labels

def month_of_year(datadic, index1=1):
    plot_data = {}
    labels = ['jan', 'feb', 'mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    
    for key1 in datadic:
        monthssum = np.zeros((12, len(datadic[key1])), dtype=float)
        monthBulkAvg = np.zeros((12, len(datadic[key1])), dtype=float)
        totalMonthsSpan = -1
        currMonth = -1
        currMonthSum, currMonthCnt = 0, 0
        for ix, d in enumerate(datadic[key1]):
            if currMonth == -1 :
                currMonth = d.month -1
            
            if currMonth != (d.month -1): #new month starts!
                totalMonthsSpan += 1
                monthBulkAvg[currMonth, totalMonthsSpan] = currMonthSum/currMonthCnt
                currMonthSum, currMonthCnt = 0, 0 
                currMonth = d.month - 1
            else:
                currMonthSum += datadic[key1][d][index1]
                currMonthCnt += 1
            monthssum[d.month - 1, ix] = datadic[key1][d][index1]
        monthBulkAvg = monthBulkAvg[:, 0:(totalMonthsSpan-1)]

        monthDeltaAvg = np.zeros(monthBulkAvg.shape, dtype=float)
        previous = np.max(monthBulkAvg[:,0])
        for ix in range(1, monthBulkAvg.shape[1]):
            month = np.argmax(monthBulkAvg[:,ix])
            monthDeltaAvg[month, ix-1] = monthBulkAvg[month,ix] - previous
            previous = monthBulkAvg[month,ix]

        monthDeltaAvg = monthDeltaAvg[:,0:monthBulkAvg.shape[1]-1]

        monthssum = monthDeltaAvg
        cnt = (monthssum != 0).sum(axis=1).ravel()
        monthssum[monthssum==0] = np.nan
        avgmonth = np.nanmean(monthssum, axis=1)
        stdmonth = np.nanstd(monthssum, axis=1)
        low = avgmonth - (1.96/np.sqrt(cnt)) * stdmonth
        high = avgmonth + (1.96/np.sqrt(cnt)) * stdmonth
        print('average delta for ', key1, ' is:', [(labels[i] +' {0:4.3f}'.format(avgmonth[i]) + ' [' + '{0:4.3f}'.format(low[i]) + ' ' + '{0:4.3f}'.format(high[i]) + ']') for i in range(0,12)])
        plot_data[key1] = avgmonth, (1.96/np.sqrt(cnt)) * stdmonth
    
    return plot_data, labels

def biweekly_of_year(datadic):
    plot_data = {}
    for key1 in datadic:
        monthssum = np.zeros((12*2, len(datadic[key1])), dtype=float)
        for ix, d in enumerate(datadic[key1]):
            month = d.month - 1
            secondhalf = 0
            day = d.day - 1; 
            if (day >=15) & (day >= 15 + (7 - d.weekday())):
                secondhalf = 1
            monthssum[ month*2 + secondhalf, ix] = datadic[key1][d][0]
        cnt = (monthssum != 0).sum(axis=1).ravel()
        monthssum[monthssum==0] = np.nan
        avgmonth = np.nanmean(monthssum, axis=1)
        stdmonth = np.nanstd(monthssum, axis=1)
        low = avgmonth - (1.96/np.sqrt(cnt)) * stdmonth
        high = avgmonth + (1.96/np.sqrt(cnt)) * stdmonth
        print(monthssum)
        print('average opening for ', key1, ' is:', [(' {0:4.3f}'.format(avgmonth[i]) + ' [' + '{0:4.3f}'.format(low[i]) + ' ' + '{0:4.3f}'.format(high[i]) + ']') for i in range(0,12)])
        plot_data[key1] = avgmonth, (1.96/np.sqrt(cnt)) * stdmonth
    labels = ['jan12','jan34','feb12','feb34','mar12','mar34','apr12','apr34','may12','may34','jun12','jun34','jul12','jul34','aug12','aug34','sep12','sep34','oct12','oct34','nov12','nov34','dec12','dec34']
    return plot_data, labels


def plot_data(plot_data, labels):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    pltlist = []
    width=0.1
    for ix, k in enumerate(plot_data):
        pltlist.append(ax.bar(np.arange(0,len(labels))-width*(ix),[i for i in plot_data[k][0]], width=width, yerr=[i for i in plot_data[k][1]]))
    ax.set_ylabel('average stock opening')
    ax.set_xticks(np.arange(0,len(labels))-width)
    ax.set_xticklabels(labels)
    ax.legend( [axxi[0] for axxi in pltlist], list(plot_data.keys()) )
    plt.show()

def run():
	d = load_data(datefrom='1-jun-2013', dateto='1-jan-2017')
	a,l = month_of_year(d, index1=0)
	plot_data(a, l)

