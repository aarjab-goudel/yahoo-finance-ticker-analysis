import pandas as pd
import time
import math
from common_service import *
from bs4 import BeautifulSoup
import requests

class CFObj:
    def __init__(self, ticker):
        self.ticker = ticker
        self.dates = []
        self.freeCashFlow = []
        self.netCashByOperatingActivities = []
        self.netCashForInvestingActivities = []
        self.netCashForFinancingActivities = []
        self.capitalExpenditures = []
    
    def getCFYahooFinancialDataUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/cash-flow?p=' + ticker

    def remove_ttm_from_cfObj(self):
        if self.dates:
            if self.dates[0].lower() == 'ttm':
                self.dates.pop(0)
                self.freeCashFlow.pop(0)
                self.netCashByOperatingActivities.pop(0)
                self.netCashForInvestingActivities.pop(0)
                self.netCashForFinancingActivities.pop(0)
                self.capitalExpenditures.pop(0)

def printCFObj(cfObj):
    print('Dates')
    print(cfObj.dates)
    print('Net Cash By Operating Activities')
    print(cfObj.netCashByOperatingActivities)
    print('Net Cash For Investing Activities')
    print(cfObj.netCashForInvestingActivities)
    print('Net Cash For Financing Activities')
    print(cfObj.netCashForFinancingActivities)
    print('Capital Expenditures')
    print(cfObj.capitalExpenditures)
    print('Free Cash Flow')
    print(cfObj.freeCashFlow)

def createErrorCFObj(ticker):
    errorCFObj = CFObj(ticker)
    errorCFObj.dates = ['0.000', '0.000', '0.000', '0.000']
    errorCFObj.freeCashFlow = ['0.000', '0.000', '0.000', '0.000']
    errorCFObj.netCashByOperatingActivities = ['0.000', '0.000', '0.000', '0.000']
    errorCFObj.netCashForInvestingActivities = ['0.000', '0.000', '0.000', '0.000']
    errorCFObj.netCashForFinancingActivities = ['0.000', '0.000', '0.000', '0.000']
    errorCFObj.capitalExpenditures = ['0.000', '0.000', '0.000', '0.000']
    return errorCFObj


def cleanCFObj(cfObj):
    cfObj.freeCashFlow = cleanRowValues(cfObj.dates, cfObj.freeCashFlow)    
    cfObj.netCashByOperatingActivities = cleanRowValues(cfObj.dates, cfObj.netCashByOperatingActivities)
    cfObj.netCashForInvestingActivities = cleanRowValues(cfObj.dates, cfObj.netCashForInvestingActivities)
    cfObj.netCashForFinancingActivities = cleanRowValues(cfObj.dates, cfObj.netCashForFinancingActivities)
    cfObj.capitalExpenditures = cleanRowValues(cfObj.dates, cfObj.capitalExpenditures) 


def readAnnualCFDataForTicker(ticker):
    cfObj = CFObj(ticker)
    
    response = requests.get(cfObj.getCFYahooFinancialDataUrl(ticker), headers=getHeader())
    print('Cash Flow Statement Response Code for ' + ticker + ' is ' + str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")


    #cfObj.dates = getRowValuesByText(soup, 'Breakdown', 'span')['Breakdown']
    cfObj.dates = readDataFromPageSource(soup, 'Breakdown', 'span')

    #cfObj.netCashByOperatingActivities = getRowValuesByText(soup, 'Operating Cash Flow', 'span')['Operating Cash Flow']
    cfObj.netCashByOperatingActivities = readDataFromPageSource(soup, 'Operating Cash Flow', 'span')

    #cfObj.netCashForInvestingActivities = getRowValuesByText(soup, 'Investing Cash Flow', 'span')['Investing Cash Flow']
    cfObj.netCashForInvestingActivities = readDataFromPageSource(soup, 'Investing Cash Flow', 'span')

    #cfObj.netCashForFinancingActivities = getRowValuesByText(soup, 'Financing Cash Flow', 'span')['Financing Cash Flow']
    cfObj.netCashForFinancingActivities = readDataFromPageSource(soup, 'Financing Cash Flow', 'span')

    #cfObj.capitalExpenditures = getRowValuesByText(soup, 'Capital Expenditure', 'span')['Capital Expenditure']
    cfObj.capitalExpenditures = readDataFromPageSource(soup, 'Capital Expenditure', 'span')

    #cfObj.freeCashFlow = getRowValuesByText(soup, 'Free Cash Flow', 'span')['Free Cash Flow']
    cfObj.freeCashFlow = readDataFromPageSource(soup, 'Free Cash Flow', 'span')

    cfObj.remove_ttm_from_cfObj()
    cleanCFObj(cfObj)
    cfObj.dates = handleEmptyDateList(cfObj.dates)
    printCFObj(cfObj)
    return cfObj


def readQuarterlyCFDataForTicker(ticker):
    cfObj = CFObj(ticker)
    
    soup = clickQuarterlyButton(cfObj.getCFYahooFinancialDataUrl(ticker))

    if soup:
       #cfObj.dates = getRowValuesByText(soup, 'Breakdown', 'span')['Breakdown']
        cfObj.dates = readDataFromPageSource(soup, 'Breakdown', 'span')

        #cfObj.netCashByOperatingActivities = getRowValuesByText(soup, 'Operating Cash Flow', 'span')['Operating Cash Flow']
        cfObj.netCashByOperatingActivities = readDataFromPageSource(soup, 'Operating Cash Flow', 'span')

        #cfObj.netCashForInvestingActivities = getRowValuesByText(soup, 'Investing Cash Flow', 'span')['Investing Cash Flow']
        cfObj.netCashForInvestingActivities = readDataFromPageSource(soup, 'Investing Cash Flow', 'span')

        #cfObj.netCashForFinancingActivities = getRowValuesByText(soup, 'Financing Cash Flow', 'span')['Financing Cash Flow']
        cfObj.netCashForFinancingActivities = readDataFromPageSource(soup, 'Financing Cash Flow', 'span')

        #cfObj.capitalExpenditures = getRowValuesByText(soup, 'Capital Expenditure', 'span')['Capital Expenditure']
        cfObj.capitalExpenditures = readDataFromPageSource(soup, 'Capital Expenditure', 'span')

        #cfObj.freeCashFlow = getRowValuesByText(soup, 'Free Cash Flow', 'span')['Free Cash Flow']
        cfObj.freeCashFlow = readDataFromPageSource(soup, 'Free Cash Flow', 'span')

        cfObj.remove_ttm_from_cfObj()
        cleanCFObj(cfObj)
        cfObj.dates = handleEmptyDateList(cfObj.dates)
        printCFObj(cfObj)
        quitDriver()
        return cfObj
    else:
        return createErrorCFObj(ticker)



