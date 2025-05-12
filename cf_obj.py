#!/usr/bin/env python3
import time
import math
from common_service import *
from bs4 import BeautifulSoup
import requests
import yfinance as yf
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

    def __repr__(self):
        return f"CFObj(ticker={self.ticker}, dates={self.dates}, freeCashFlow={self.freeCashFlow}, netCashByOps={self.netCashByOperatingActivities}, netCashForInvest={self.netCashForInvestingActivities}, netCashForFinanceing={self.netCashForFinancingActivities}, capitalExpenditure={self.capitalExpenditures})"

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


    cfObj.dates = readDataFromPageSource(soup, 'Breakdown', False)

    cfObj.netCashByOperatingActivities = readDataFromPageSource(soup, 'Operating Cash Flow', False)

    cfObj.netCashForInvestingActivities = readDataFromPageSource(soup, 'Investing Cash Flow', False)

    cfObj.netCashForFinancingActivities = readDataFromPageSource(soup, 'Financing Cash Flow', False)

    cfObj.capitalExpenditures = readDataFromPageSource(soup, 'Capital Expenditure', False)

    cfObj.freeCashFlow = readDataFromPageSource(soup, 'Free Cash Flow', False)

    cfObj.remove_ttm_from_cfObj()
    cleanCFObj(cfObj)
    cfObj.dates = handleEmptyDateList(cfObj.dates)
    printCFObj(cfObj)
    return cfObj


def readQuarterlyCFDataForTicker(ticker):
    cfObj = CFObj(ticker)
    page = open_browser()
    soup = clickQuarterlyButton(page, cfObj.getCFYahooFinancialDataUrl(ticker))

    if soup:
        cfObj.dates = readDataFromPageSource(soup, 'Breakdown', True)

        cfObj.netCashByOperatingActivities = readDataFromPageSource(soup, 'Operating Cash Flow', True)

        cfObj.netCashForInvestingActivities = readDataFromPageSource(soup, 'Investing Cash Flow', True)

        cfObj.netCashForFinancingActivities = readDataFromPageSource(soup, 'Financing Cash Flow', True)

        cfObj.capitalExpenditures = readDataFromPageSource(soup, 'Capital Expenditure', True)

        cfObj.freeCashFlow = readDataFromPageSource(soup, 'Free Cash Flow', True)

        cfObj.remove_ttm_from_cfObj()
        cleanCFObj(cfObj)
        cfObj.dates = handleEmptyDateList(cfObj.dates)
        printCFObj(cfObj)
        return cfObj
    else:
        return createErrorCFObj(ticker)
    

def readAnnualCFDataWithYFinance(ticker, history_years=4):
    """
    Fetch annual cash‐flow history for `ticker` via yfinance only.
    Uses these exact row labels from df.index:
      - Free Cash Flow
      - Operating Cash Flow
      - Investing Cash Flow
      - Financing Cash Flow
      - Capital Expenditure
    """
    cfObj = CFObj(ticker)
    df    = yf.Ticker(ticker).cashflow

    # 1) grab the up-to-N most recent period-ending dates
    cfObj.dates = normalize([c.strftime("%Y-%m-%d") for c in df.columns][:history_years])

    # 2) helper to pull & clean a single row by its exact label
    def get_row_exact(label):
        if label not in df.index:
            raise KeyError(
                f"Row '{label}' not found; available rows: {df.index.tolist()}"
            )
        series = (
            df.loc[label]
              .infer_objects(copy=False)
              .fillna(0)
              .astype(float)
        )
        return series.tolist()[:history_years]

    cfObj.freeCashFlow                   = normalize(get_row_exact("Free Cash Flow"))
    cfObj.netCashByOperatingActivities   = normalize(get_row_exact("Operating Cash Flow"))
    cfObj.netCashForInvestingActivities  = normalize(get_row_exact("Investing Cash Flow"))
    cfObj.netCashForFinancingActivities  = normalize(get_row_exact("Financing Cash Flow"))
    cfObj.capitalExpenditures            = normalize(get_row_exact("Capital Expenditure"))

    # debug prints (optional)
    print("dates:",                          cfObj.dates)
    print("freeCashFlow:",                   cfObj.freeCashFlow)
    print("netCashByOperatingActivities:",   cfObj.netCashByOperatingActivities)
    print("netCashForInvestingActivities:",  cfObj.netCashForInvestingActivities)
    print("netCashForFinancingActivities:",  cfObj.netCashForFinancingActivities)
    print("capitalExpenditures:",            cfObj.capitalExpenditures)

    return cfObj


def readQuarterlyCFDataWithYFinance(ticker, history_quarters=5):
    """
    Fetch quarterly cash‐flow history for `ticker` via yfinance only.
    Uses these exact row labels from df.index:
      - Free Cash Flow
      - Operating Cash Flow
      - Investing Cash Flow
      - Financing Cash Flow
      - Capital Expenditure

    Returns a CFObj with:
      - dates (last N quarter-end YYYY-MM-DD)
      - freeCashFlow
      - netCashByOperatingActivities
      - netCashForInvestingActivities
      - netCashForFinancingActivities
      - capitalExpenditures
    """
    cfObj = CFObj(ticker)
    df    = yf.Ticker(ticker).quarterly_cashflow

    # 1) grab the up-to-N most recent quarter-ending dates
    cfObj.dates = normalize([c.strftime("%Y-%m-%d") for c in df.columns][:history_quarters])

    # 2) helper to pull & clean a single row by its exact label
    def get_row_exact(label):
        if label not in df.index:
            raise KeyError(
                f"Row '{label}' not found; available rows: {df.index.tolist()}"
            )
        series = (
            df.loc[label]
              .infer_objects(copy=False)
              .fillna(0)
              .astype(float)
        )
        return series.tolist()[:history_quarters]

    # 3) populate each CFObj field
    cfObj.freeCashFlow                   = normalize(get_row_exact("Free Cash Flow"))
    cfObj.netCashByOperatingActivities   = normalize(get_row_exact("Operating Cash Flow"))
    cfObj.netCashForInvestingActivities  = normalize(get_row_exact("Investing Cash Flow"))
    cfObj.netCashForFinancingActivities  = normalize(get_row_exact("Financing Cash Flow"))
    cfObj.capitalExpenditures            = normalize(get_row_exact("Capital Expenditure"))

    # debug prints (optional)
    print("quarterly dates:",                         cfObj.dates)
    print("freeCashFlow:",                            cfObj.freeCashFlow)
    print("netCashByOperatingActivities:",            cfObj.netCashByOperatingActivities)
    print("netCashForInvestingActivities:",           cfObj.netCashForInvestingActivities)
    print("netCashForFinancingActivities:",           cfObj.netCashForFinancingActivities)
    print("capitalExpenditures:",                     cfObj.capitalExpenditures)

    return cfObj



if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    quarterlyCFObj = readQuarterlyCFDataWithYFinance(args.ticker)
    annualCFObj = readAnnualCFDataWithYFinance(args.ticker)



