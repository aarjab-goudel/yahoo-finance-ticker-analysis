#!/usr/bin/env python3
import time
import math
import requests
from bs4 import BeautifulSoup
from common_service import *
import yfinance as yf
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
    url = bsObj.getBSYahooFinancialDataUrl(ticker)
    response = requests.get(bsObj.getBSYahooFinancialDataUrl(ticker), headers=getHeader())
    print("Fetching:", url)
    print("→ Status code:", response.status_code)
    print("→ Headers:", response.headers)
    print("→ History:", response.history)       # any redirects?
    print("→ Body snippet:", response.text[:500])
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

        if ev_ebitda:
            ev_ebitda.pop(0)
            bsObj.ev_ebitda = ev_ebitda
        else:
            bsObj.ev_ebitda = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']

        if ev_ebitda_dates:
            ev_ebitda_dates.pop(0)
            bsObj.ev_ebitda_dates = ev_ebitda_dates
        else:
            bsObj.ev_ebitda_dates = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']

        if peg_ratios:
            peg_ratios.pop(0)
            bsObj.peg_ratios = peg_ratios
        else:
            bsObj.peg_ratios = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']


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

        if ev_ebitda:
            ev_ebitda.pop(0)
            bsObj.ev_ebitda = ev_ebitda
        else:
            bsObj.ev_ebitda = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']

        if ev_ebitda_dates:
            ev_ebitda_dates.pop(0)
            bsObj.ev_ebitda_dates = ev_ebitda_dates
        else:
            bsObj.ev_ebitda_dates = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']

        if peg_ratios:
            peg_ratios.pop(0)
            bsObj.peg_ratios = peg_ratios
        else:
            bsObj.peg_ratios = ['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR']
        



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



def readAnnualBSDataWithYFinance(ticker, history_years=4):
    """
    Fetch annual BS history for `ticker` via yfinance only.
    - dates:              list of YYYY-MM-DD (up to history_years)
    - totalAssets:        list of floats
    - totalLiabilities:   list of floats (Net Minority Interest)
    - totalEquity:        list of floats (Gross Minority Interest)
    - totalCash:          list of floats (Cash And Cash Equivalents)
    - totalDebt:          list of floats (Short + Long Term Debt)
    - currentRatio:       string
    - ev_ebitda:          list with single float [current EV/EBITDA]
    - ev_ebitda_dates:    ["Current"]
    - peg_ratios:         list with single float [current PEG]
    """
    t  = yf.Ticker(ticker)
    bs = t.balance_sheet

    # 1) Period-ending dates
    dates = [c.strftime("%Y-%m-%d") for c in bs.columns][:history_years]

    # 2) Helper to pull & clean each row
    def get_row(name):
        if name in bs.index:
            series = bs.loc[name].infer_objects(copy=False).fillna(0)
            return series.astype(float).tolist()[:history_years]
        return [0.0] * len(dates)

    totalAssets      = get_row("Total Assets")
    totalLiabilities = get_row("Total Liabilities Net Minority Interest")
    totalEquity      = get_row("Total Equity Gross Minority Interest")
    totalCash        = get_row("Cash And Cash Equivalents")

    # build totalDebt = short-term + long-term
    short_debt = get_row("Short Long Term Debt")
    long_debt  = get_row("Long Term Debt")
    totalDebt  = [s + l for s, l in zip(short_debt, long_debt)]

    # 3) Ratios from t.info()
    info        = t.info or {}
    currentRatio= str(info.get("currentRatio", 0))

    ev_value    = info.get("enterpriseToEbitda", None)
    peg_value   = info.get("pegRatio",         None)

    ev_ebitda      = [ev_value] if ev_value is not None else []
    ev_ebitda_dates= ["Current"] if ev_value is not None else []
    peg_ratios     = [peg_value] if peg_value is not None else []

    # 4) Pack into BSObj
    bsObj = BSObj(ticker)
    bsObj.dates            = normalize_dates(dates, False)
    bsObj.totalAssets      = normalize(totalAssets, False) 
    bsObj.totalLiabilities = normalize(totalLiabilities, False) 
    bsObj.totalEquity      = normalize(totalEquity, False)
    bsObj.totalCash        = normalize(totalCash, False)
    bsObj.totalDebt        = normalize(totalDebt, False)
    bsObj.currentRatio     = currentRatio
    bsObj.ev_ebitda        = ev_ebitda
    bsObj.ev_ebitda_dates  = ev_ebitda_dates
    bsObj.peg_ratios       = peg_ratios

    print("dates:",            bsObj.dates)
    print("totalAssets:",      bsObj.totalAssets)
    print("totalLiabilities:", bsObj.totalLiabilities)
    print("totalEquity:",      bsObj.totalEquity)
    print("totalCash:",        bsObj.totalCash)
    print("totalDebt:",        bsObj.totalDebt)
    print("currentRatio:",     bsObj.currentRatio)
    print("ev_ebitda:",        bsObj.ev_ebitda)
    print("ev_ebitda_dates:",  bsObj.ev_ebitda_dates)
    print("peg_ratios:",       bsObj.peg_ratios)

    return bsObj


def readQuarterlyBSDataWithYFinance(ticker, history_quarters=5):
    """
    Fetch quarterly BS history for `ticker` via yfinance only.
    - dates:              list of YYYY-MM-DD (up to history_quarters most recent)
    - totalAssets:        list of floats
    - totalLiabilities:   list of floats (Net Minority Interest)
    - totalEquity:        list of floats (Gross Minority Interest)
    - totalCash:          list of floats (Cash And Cash Equivalents)
    - totalDebt:          list of floats (Short + Long Term Debt)
    - currentRatio:       string (from t.info)
    - ev_ebitda:          list with single float [current EV/EBITDA]
    - ev_ebitda_dates:    ["Current"]
    - peg_ratios:         list with single float [current PEG]
    """
    t   = yf.Ticker(ticker)
    qbs = t.quarterly_balance_sheet

    # 1) grab the N most recent quarter-end dates
    dates = [c.strftime("%Y-%m-%d") for c in qbs.columns][:history_quarters]

    # 2) safe row-getter for the quarterly frame
    def get_row(name):
        if name in qbs.index:
            s = qbs.loc[name].infer_objects(copy=False).fillna(0)
            return s.astype(float).tolist()[:history_quarters]
        return [0.0] * len(dates)

    # 3) pull your core rows
    totalAssets      = get_row("Total Assets")
    totalLiabilities = get_row("Total Liabilities Net Minority Interest")
    totalEquity      = get_row("Total Equity Gross Minority Interest")
    totalCash        = get_row("Cash And Cash Equivalents")

    # 4) build debt = short + long
    short_debt = get_row("Short Long Term Debt")
    long_debt  = get_row("Long Term Debt")
    totalDebt  = [s + l for s, l in zip(short_debt, long_debt)]

    # 5) ratios/current values from info()
    info         = t.info or {}
    currentRatio = str(info.get("currentRatio", 0))
    ev_value     = info.get("enterpriseToEbitda", None)
    peg_value    = info.get("pegRatio",         None)

    ev_ebitda       = [ev_value] if ev_value is not None else []
    ev_ebitda_dates = ["Current"] if ev_value is not None else []
    peg_ratios      = [peg_value] if peg_value is not None else []

    # 6) pack into BSObj
    bsObj = BSObj(ticker)
    bsObj.dates            = normalize_dates(dates, True)
    bsObj.totalAssets      = normalize(totalAssets, True) 
    bsObj.totalLiabilities = normalize(totalLiabilities, True) 
    bsObj.totalEquity      = normalize(totalEquity, True)
    bsObj.totalCash        = normalize(totalCash, True)
    bsObj.totalDebt        = normalize(totalDebt, True)
    bsObj.currentRatio     = currentRatio
    bsObj.ev_ebitda        = ev_ebitda
    bsObj.ev_ebitda_dates  = ev_ebitda_dates
    bsObj.peg_ratios       = peg_ratios

    print("dates:",            bsObj.dates)
    print("totalAssets:",      bsObj.totalAssets)
    print("totalLiabilities:", bsObj.totalLiabilities)
    print("totalEquity:",      bsObj.totalEquity)
    print("totalCash:",        bsObj.totalCash)
    print("totalDebt:",        bsObj.totalDebt)
    print("currentRatio:",     bsObj.currentRatio)
    print("ev_ebitda:",        bsObj.ev_ebitda)
    print("ev_ebitda_dates:",  bsObj.ev_ebitda_dates)
    print("peg_ratios:",       bsObj.peg_ratios)

    return bsObj




if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    quarterlyBSObj = readQuarterlyBSDataWithYFinance(args.ticker)
    annualBSObj = readAnnualBSDataWithYFinance(args.ticker)



