import time
import math
import requests
from bs4 import BeautifulSoup
from common_service import *
class BSObj:
    def __init__(self, ticker):
        self.ticker = ticker
        self.dates = []
        self.totalAssets = []
        self.totalLiabilities = []
        self.totalEquity = []
        self.totalCash = ''
        self.totalDebt = ''
        self.currentRatio = ''



    def getBSYahooFinancialDataUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/balance-sheet?p=' + ticker

    def getStatisticsDataUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker


def printBSObj(bsObj):
    print('Dates')
    print(bsObj.dates)
    print('Total Assets')
    print(bsObj.totalAssets)
    print('Total Liabilities')
    print(bsObj.totalLiabilities)
    print('Total Equity')
    print(bsObj.totalEquity)
    print('Total Cash')
    print(bsObj.totalCash)
    print('Total Debt')
    print(bsObj.totalDebt)
    print('Current Ratio')
    print(bsObj.currentRatio)

def createErrorBSObj(ticker):
    errorBSObj = BSObj(ticker)
    errorBSObj.dates = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalAssets = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalLiabilities = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalEquity = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalCash = '0.000'
    errorBSObj.totalDebt = '0.000'
    errorBSObj.currentRatio = '0.000'
    return errorBSObj

def cleanBSObj(bsObj):
    bsObj.totalAssets = cleanRowValues(bsObj.dates, bsObj.totalAssets)    
    bsObj.totalLiabilities = cleanRowValues(bsObj.dates, bsObj.totalLiabilities)
    bsObj.totalEquity = cleanRowValues(bsObj.dates, bsObj.totalEquity)



def readAnnualBSDataForTicker(ticker):
    bsObj = BSObj(ticker)
    
    response = requests.get(bsObj.getBSYahooFinancialDataUrl(ticker), headers=getHeader())
    print('Balance Sheet Response Code for ' + ticker + ' is ' + str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")

    #bsObj.dates = getRowValuesByText(soup, 'Breakdown', 'span')['Breakdown']
    bsObj.dates = readDataFromPageSource(soup, 'Breakdown', 'span')
    bsObj.dates = handleEmptyDateList(bsObj.dates)

    #bsObj.totalAssets = getRowValuesByText(soup, 'Total Assets', 'span')['Total Assets']
    bsObj.totalAssets = readDataFromPageSource(soup, 'Total Assets', 'span')

    #bsObj.totalLiabilities = getRowValuesByText(soup, 'Total Liabilities Net Minority Interest', 'span')['Total Liabilities Net Minority Interest']
    bsObj.totalLiabilities = readDataFromPageSource(soup, 'Total Liabilities Net Minority Interest', 'span')

    #bsObj.totalEquity = getRowValuesByText(soup, 'Total Equity Gross Minority Interest', 'span')['Total Equity Gross Minority Interest']
    bsObj.totalEquity = readDataFromPageSource(soup, 'Total Equity Gross Minority Interest', 'span')

    response = requests.get(bsObj.getStatisticsDataUrl(ticker), headers=getHeader())
    print('Balance Sheet Statistics Response Code for ' + ticker + ' is ' + str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        bsObj.totalCash = getRowValueFromStatisticsRow(soup, 'Total Cash', 'span')['Total Cash']
        bsObj.totalDebt = getRowValueFromStatisticsRow(soup, 'Total Debt', 'span')['Total Debt']
        bsObj.currentRatio = getRowValueFromStatisticsRow(soup, 'Current Ratio', 'span')['Current Ratio']
    except Exception as e:
        print(e)
        bsObj.totalCash = '0.000'
        bsObj.totalDebt = '0.000'
        bsObj.currentRatio = '0.000'


    cleanBSObj(bsObj)
    bsObj.dates = handleEmptyDateList(bsObj.dates)
    printBSObj(bsObj)
    return bsObj

def readQuarterlyBSDataForTicker(ticker):
    bsObj = BSObj(ticker)

    soup = clickQuarterlyButton(bsObj.getBSYahooFinancialDataUrl(ticker))

    if soup:
        #bsObj.dates = getRowValuesByText(soup, 'Breakdown', 'span')['Breakdown']
        bsObj.dates = readDataFromPageSource(soup, 'Breakdown', 'span')

        #bsObj.totalAssets = getRowValuesByText(soup, 'Total Assets', 'span')['Total Assets']
        bsObj.totalAssets = readDataFromPageSource(soup, 'Total Assets', 'span')

        #bsObj.totalLiabilities = getRowValuesByText(soup, 'Total Liabilities Net Minority Interest', 'span')['Total Liabilities Net Minority Interest']
        bsObj.totalLiabilities = readDataFromPageSource(soup, 'Total Liabilities Net Minority Interest', 'span')

       #bsObj.totalEquity = getRowValuesByText(soup, 'Total Equity Gross Minority Interest', 'span')['Total Equity Gross Minority Interest']
        bsObj.totalEquity = readDataFromPageSource(soup, 'Total Equity Gross Minority Interest', 'span')

        quitDriver()
        cleanBSObj(bsObj)
        bsObj.dates = handleEmptyDateList(bsObj.dates)
        printBSObj(bsObj)
        return bsObj
    else:
        return createErrorBSObj(ticker)


