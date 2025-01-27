#!/usr/bin/env python3
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
        self.ev_ebitda = []
        self.ev_ebitda_dates = []
        self.peg_ratios = []

    def __repr__(self):
        return f"BSObj(ticker={self.ticker}, dates={self.dates}, totalAssets={self.totalAssets}, totalLiab={self.totalLiabilities}, totalEquity={self.totalEquity}, totalCash={self.totalCash}, totalDebt={self.totalDebt}, currRatio={self.currentRatio})"

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
    print('EV/EBITDA')
    print(bsObj.ev_ebitda)
    print('EV/EBITDA dates')
    print(bsObj.ev_ebitda_dates)
    print('PEG Ratios')
    print(bsObj.peg_ratios)

def createErrorBSObj(ticker):
    errorBSObj = BSObj(ticker)
    errorBSObj.dates = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalAssets = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalLiabilities = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalEquity = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.totalCash = '0.000'
    errorBSObj.totalDebt = '0.000'
    errorBSObj.currentRatio = '0.000'
    errorBSObj.peg_ratios = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.ev_ebitda = ['0.000', '0.000', '0.000', '0.000']
    errorBSObj.ev_ebitda_dates = ['0.000', '0.000', '0.000', '0.000']
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


    bsObj.dates = readDataFromPageSource(soup, 'Breakdown', False)
    bsObj.dates = handleEmptyDateList(bsObj.dates)

    bsObj.totalAssets = readDataFromPageSource(soup, 'Total Assets', False)

    bsObj.totalLiabilities = readDataFromPageSource(soup, 'Total Liabilities Net Minority Interest', False)

    bsObj.totalEquity = readDataFromPageSource(soup, 'Total Equity Gross Minority Interest', False)

    response = requests.get(bsObj.getStatisticsDataUrl(ticker), headers=getHeader())
    print('Balance Sheet Statistics Response Code for ' + ticker + ' is ' + str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        bsObj.totalCash = getRowValueFromStatisticsRow(soup, 'Total Cash')['Total Cash']
        bsObj.totalDebt = getRowValueFromStatisticsRow(soup, 'Total Debt')['Total Debt']
        bsObj.currentRatio = getRowValueFromStatisticsRow(soup, 'Current Ratio')['Current Ratio']
        ev_ebitda = getStatisticsTableByText(soup, "Enterprise Value/EBITDA")
        ev_ebitda_dates = getStatisticsDatesByText(soup, "Current")
        peg_ratios = getPEGRatios(soup)
        peg_ratios.pop(0)
        ev_ebitda.pop(0)
        ev_ebitda_dates.pop(0)
        bsObj.ev_ebitda = ev_ebitda
        bsObj.ev_ebitda_dates = ev_ebitda_dates
        bsObj.peg_ratios = peg_ratios


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
    page = open_browser()

    statistics_response = requests.get(bsObj.getStatisticsDataUrl(ticker), headers=getHeader())
    statistics_soup = BeautifulSoup(statistics_response.content, "html.parser")

    if statistics_soup:
        ev_ebitda = getStatisticsTableByText(statistics_soup, "Enterprise Value/EBITDA")
        ev_ebitda_dates = getStatisticsDatesByText(statistics_soup, "Current")
        peg_ratios = getPEGRatios(statistics_soup)
        peg_ratios.pop(0)
        ev_ebitda.pop(0)
        ev_ebitda_dates.pop(0)
        bsObj.ev_ebitda = ev_ebitda
        bsObj.ev_ebitda_dates = ev_ebitda_dates
        bsObj.peg_ratios = peg_ratios



    soup = clickQuarterlyButton(page, bsObj.getBSYahooFinancialDataUrl(ticker))

    if soup:
        bsObj.dates = readDataFromPageSource(soup, 'Breakdown', True)

        bsObj.totalAssets = readDataFromPageSource(soup, 'Total Assets', True)

        bsObj.totalLiabilities = readDataFromPageSource(soup, 'Total Liabilities Net Minority Interest', True)

        bsObj.totalEquity = readDataFromPageSource(soup, 'Total Equity Gross Minority Interest', True)

        cleanBSObj(bsObj)
        bsObj.dates = handleEmptyDateList(bsObj.dates)
        printBSObj(bsObj)
        return bsObj
    else:
        return createErrorBSObj(ticker)

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    bsObj = readAnnualBSDataForTicker(args.ticker)


