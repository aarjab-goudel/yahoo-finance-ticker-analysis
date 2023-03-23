import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as ur
import requests
from urllib.request import Request, urlopen

class FutureStockObj:
    def __init__(self, ticker):
        self.ticker = ticker
        self.currentYear = ''
        self.nextYear = ''
        self.currentYearEPS = ''
        self.nextYearEPS = ''
        self.currentYearRev = ''
        self.nextYearRev = ''

    def getFutureAnalysisUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/analysis?p=' + ticker

def printFutureStockObj(futureStockObj):
    print('Current Year')
    print(futureStockObj.currentYear)
    print('Next Year')
    print(futureStockObj.nextYear)
    print('Current Year EPS')
    print(futureStockObj.currentYearEPS)
    print('Next Year EPS')
    print(futureStockObj.nextYearEPS)
    print('Current Year Revenue')
    print(futureStockObj.currentYearRev)
    print('Next Year Revenue')
    print(futureStockObj.nextYearRev)

def readFutureStockData(ticker):
    futureStockObj = FutureStockObj(ticker)
    try:
        url = futureStockObj.getFutureAnalysisUrl(ticker)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        read_data = urlopen(req).read()
        soup_is = BeautifulSoup(read_data, 'lxml')
        ls= [] 
        for element in soup_is.find_all('table'): 
            ls.append(element) # add each element one by one to the list

        earningsSpanTags = ls[0].find_all('span')
        futureStockObj.currentYear = earningsSpanTags[7].get_text()
        futureStockObj.nextYear = earningsSpanTags[9].get_text()

        earningsTRTags = ls[0].find_all('tr')
        futureStockObj.currentYearEPS = earningsTRTags[2].find_all('td')[3].get_text()
        futureStockObj.nextYearEPS = earningsTRTags[2].find_all('td')[4].get_text()

        revenueTable = ls[1].find_all('tr')
        futureStockObj.currentYearRev = revenueTable[2].find_all('td')[3].get_text()
        futureStockObj.nextYearRev = revenueTable[2].find_all('td')[4].get_text()
    except Exception as e:
        print(e)
        futureStockObj.currentYear = '0.000'
        futureStockObj.nextYear = '0.000'
        futureStockObj.currentYearEPS = '0.000'
        futureStockObj.nextYearEPS = '0.000'
        futureStockObj.currentYearRev = '0.000'
        futureStockObj.nextYearRev = '0.000'
    

    return futureStockObj
        
    





