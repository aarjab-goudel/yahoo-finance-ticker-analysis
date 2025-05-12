#!/usr/bin/env python3
from bs4 import BeautifulSoup
import urllib.request as ur
import requests
from urllib.request import Request, urlopen
from common_service import *
import yfinance as yf
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

    def __repr__(self):
        return f"FutureStockObj(ticker={self.ticker}, currentYear={self.currentYear}, nextYear={self.nextYear}, currentYearEPS={self.currentYearEPS}, nextYearEPS={self.nextYearEPS}, currentYearRev={self.currentYearRev}, nextYearRev={self.nextYearRev})"

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


def readFutureStockDataWithYFinance(ticker):
    """
    Fetch forward-looking EPS and revenue estimates for `ticker` via yfinance only,
    pulling the 'avg' column at the '0y' and '+1y' rows:

      - '0y'  = current-year
      - '+1y' = next-year
    """
    fso = FutureStockObj(ticker)
    t   = yf.Ticker(ticker)

    # pull the two tables
    ee = t.earnings_estimate    # EPS estimates
    re = t.revenue_estimate     # revenue estimates

    # debug
    print("[DEBUG] earnings_estimate index:", ee.index.tolist())
    print("[DEBUG] earnings_estimate columns:", ee.columns.tolist())
    print("[DEBUG] revenue_estimate index:", re.index.tolist())
    print("[DEBUG] revenue_estimate columns:", re.columns.tolist())

    # the consensus column
    col = "avg"

    # rows for current vs next year
    curr_row = "0y"
    next_row = "+1y"

    # sanity checks
    for df, name in [(ee, "EPS"), (re, "Revenue")]:
        if curr_row not in df.index or next_row not in df.index:
            raise KeyError(f"Could not find rows {curr_row!r} / {next_row!r} in {name} estimate index {df.index.tolist()}")
        if col not in df.columns:
            raise KeyError(f"Could not find column {col!r} in {name} estimate columns {df.columns.tolist()}")

    # friendly labels
    fso.currentYear = "Current Year"
    fso.nextYear    = "Next Year"

    # extract
    fso.currentYearEPS = str(ee.at[curr_row, col])
    fso.nextYearEPS    = str(ee.at[next_row, col])
    fso.currentYearRev = str(re.at[curr_row, col] / 1_000)
    fso.nextYearRev    = str(re.at[next_row, col] / 1_000)

    # final debug
    print(f"[DEBUG] {ticker} → EPS avg: 0y={fso.currentYearEPS}, +1y={fso.nextYearEPS}")
    print(f"[DEBUG] {ticker} → Rev avg: 0y={fso.currentYearRev}, +1y={fso.nextYearRev}")

    return fso


def readFutureStockData(ticker):
    futureStockObj = FutureStockObj(ticker)
    try:
        response = requests.get(futureStockObj.getFutureAnalysisUrl(ticker), headers=getHeader())
        soup = BeautifulSoup(response.content, "html.parser")
        if soup:
            divs = soup.find_all("div", class_="tableContainer")
            index = 0
            for div in divs:
                if index < 2:
                    ths = div.find_all("th")
                    for th in ths:
                        text = th.get_text(strip=True)
                        if 'Current Year' in text:
                            futureStockObj.currentYear = text
                        if 'Next Year' in text:
                            futureStockObj.nextYear = text
                    
                    tds = div.find_all("td")
                    table_index = 0
                    for td in tds:
                        text = td.get_text(strip=True)
                        if table_index == 8:
                            if index == 0:
                                futureStockObj.currentYearEPS = text
                            if index == 1:
                                futureStockObj.currentYearRev = text
                        if table_index == 9:
                            if index == 0:
                                futureStockObj.nextYearEPS = text
                            if index == 1:
                                futureStockObj.nextYearRev = text
                        table_index = table_index + 1
                index = index + 1
        
        printFutureStockObj(futureStockObj)
    except Exception as e:
        print(e)
        futureStockObj.currentYear = '0.000'
        futureStockObj.nextYear = '0.000'
        futureStockObj.currentYearEPS = '0.000'
        futureStockObj.nextYearEPS = '0.000'
        futureStockObj.currentYearRev = '0.000'
        futureStockObj.nextYearRev = '0.000'
    

    return futureStockObj

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    bsObj = readFutureStockDataWithYFinance(args.ticker)
        
    





