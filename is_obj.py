#!/usr/bin/env python3
import time
import math
from common_service import *
from bs4 import BeautifulSoup
import requests
import yfinance as yf
class ISObj:
    def __init__(self, ticker):
        self.ticker = ticker
        self.dates = []
        self.revenue = []
        self.costOfRevenue = []
        self.grossProfit = []
        self.operatingIncome = []
        self.netIncome = []
        self.researchAndDevelopment = []
        self.ebitda = []
        self.interestExpense = []
        
    def getISYahooFinancialDataUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/financials?p=' + ticker

    def __repr__(self):
        return f"ISObj(ticker={self.ticker}, dates={self.dates}, revenue={self.revenue}, costOfRevenue={self.costOfRevenue}, grossProfit={self.grossProfit}, operatingIncome={self.operatingIncome}, netIncome={self.netIncome}, R&D={self.researchAndDevelopment}, EBITDA={self.ebitda})"

    def remove_ttm_from_isObj(self):
        if self.dates:
            if self.dates[0].lower() == 'ttm':
                self.dates.pop(0)
                self.revenue.pop(0)
                self.costOfRevenue.pop(0)
                self.grossProfit.pop(0)
                self.operatingIncome.pop(0)
                self.netIncome.pop(0)
                self.researchAndDevelopment.pop(0)
                self.ebitda.pop(0)
                self.interestExpense.pop(0)

    def remove_string_from_num_list(self, num_list):
        for item in num_list.copy():
            if not is_valid_number(item):
                num_list.remove(item)
        

def cleanISObj(isObj):
    isObj.revenue = cleanRowValues(isObj.dates, isObj.revenue)    
    isObj.costOfRevenue = cleanRowValues(isObj.dates, isObj.costOfRevenue)
    isObj.grossProfit = cleanRowValues(isObj.dates, isObj.grossProfit)
    isObj.operatingIncome = cleanRowValues(isObj.dates, isObj.operatingIncome)
    isObj.netIncome = cleanRowValues(isObj.dates, isObj.netIncome)
    isObj.researchAndDevelopment = cleanRowValues(isObj.dates, isObj.researchAndDevelopment)     
    isObj.ebitda = cleanRowValues(isObj.dates, isObj.ebitda)
    isObj.interestExpense = cleanRowValues(isObj.dates, isObj.interestExpense)       


def printISObj(isObj):
    print('Dates')
    print(isObj.dates)
    print('Revenue')
    print(isObj.revenue)
    print('Cost of Revenue')
    print(isObj.costOfRevenue)
    print('Gross Profit')
    print(isObj.grossProfit)
    print('Operating Income')
    print(isObj.operatingIncome)
    print('netIncome')
    print(isObj.netIncome)
    print('Research And Development')
    print(isObj.researchAndDevelopment)
    print('EBITDA')
    print(isObj.ebitda)
    print('Interest Expense')
    print(isObj.interestExpense)

def remove_all_text_from_isObj(isObj):
    isObj.remove_string_from_num_list(isObj.revenue)
    isObj.remove_string_from_num_list(isObj.costOfRevenue)
    isObj.remove_string_from_num_list(isObj.grossProfit)
    isObj.remove_string_from_num_list(isObj.operatingIncome)
    isObj.remove_string_from_num_list(isObj.netIncome)
    isObj.remove_string_from_num_list(isObj.researchAndDevelopment)
    isObj.remove_string_from_num_list(isObj.ebitda)
    isObj.remove_string_from_num_list(isObj.interestExpense)

def create_quarterly_research_and_dev_list(dates):
    q_r_d_list = []
    if dates:
        for date in dates:
            q_r_d_list.append('0.000')
    return q_r_d_list

def createErrorISObj(ticker):
    errorISObj = ISObj(ticker)
    errorISObj.dates = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.revenue = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.costOfRevenue = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.grossProfit = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.operatingIncome = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.netIncome = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.researchAndDevelopment = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.ebitda = ['0.000', '0.000', '0.000', '0.000']
    errorISObj.interestExpense = ['0.000', '0.000', '0.000', '0.000']
    return errorISObj

 

def readAnnualISDataForTicker(ticker):
    isObj = ISObj(ticker)
    
    response = requests.get(isObj.getISYahooFinancialDataUrl(ticker), headers=getHeader())
    print('Income Statement Response Code for ' + ticker + ' is ' + str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")

    isObj.dates = readDataFromPageSource(soup, 'Breakdown', False)

    isObj.revenue = readDataFromPageSource(soup, 'Total Revenue', False)

    isObj.costOfRevenue = readDataFromPageSource(soup, 'Cost of Revenue', False)

    isObj.grossProfit = readDataFromPageSource(soup, 'Gross Profit', False)

    isObj.operatingIncome = readDataFromPageSource(soup, 'Operating Income', False)

    isObj.netIncome = readDataFromPageSource(soup, 'Net Income from Continuing & Discontinued Operation', False)

    isObj.ebitda = readDataFromPageSource(soup, 'EBITDA', False)

    isObj.interestExpense = readDataFromPageSource(soup, 'Interest Expense', False)


    page = open_browser()
    r_and_d_soup = clickOperatingExpense(page, isObj.getISYahooFinancialDataUrl(ticker))
    if r_and_d_soup:
        isObj.researchAndDevelopment = readDataFromPageSource(r_and_d_soup, 'Research & Development', False)
    else:
        isObj.researchAndDevelopment = ['0.000', '0.000', '0.000', '0.000']
 
 
    remove_all_text_from_isObj(isObj)
    isObj.remove_ttm_from_isObj()
    cleanISObj(isObj)
    isObj.dates = handleEmptyDateList(isObj.dates)
    printISObj(isObj)
    return isObj

def readQuarterlyISDataForTicker(ticker):
    isObj = ISObj(ticker)
    page = open_browser()

    
    soup = clickQuarterlyButton(page, isObj.getISYahooFinancialDataUrl(ticker))

    if soup:
        isObj.dates = readDataFromPageSource(soup, 'Breakdown', True)

        isObj.revenue = readDataFromPageSource(soup, 'Total Revenue', True)

        isObj.costOfRevenue = readDataFromPageSource(soup, 'Cost of Revenue', True)

        isObj.grossProfit = readDataFromPageSource(soup, 'Gross Profit', True)

        isObj.operatingIncome = readDataFromPageSource(soup, 'Operating Income', True)

        isObj.netIncome = readDataFromPageSource(soup, 'Net Income from Continuing & Discontinued Operation', True)

        isObj.ebitda = readDataFromPageSource(soup, 'EBITDA', True)

        isObj.interestExpense = readDataFromPageSource(soup, 'Interest Expense', True)

        isObj.researchAndDevelopment = create_quarterly_research_and_dev_list(isObj.dates)
        remove_all_text_from_isObj(isObj)
        isObj.remove_ttm_from_isObj()
        cleanISObj(isObj)
        isObj.dates = handleEmptyDateList(isObj.dates)
        printISObj(isObj)
        return isObj
    else:
        return createErrorISObj(ticker)
    
def readAnnualISDataWithYFinance(ticker, history_years=4):
    """
    Fetch annual income‐statement history for `ticker` via yfinance only.
    Populates ISObj with exactly these row labels from df.index:
      - Total Revenue
      - Cost Of Revenue
      - Gross Profit
      - Operating Income
      - Net Income
      - Research & Development
      - EBITDA
      - Interest Expense
    """
    isObj = ISObj(ticker)
    df    = yf.Ticker(ticker).financials

    # 1) grab the up-to-N most recent period-ending dates
    isObj.dates = [c.strftime("%Y-%m-%d") for c in df.columns][:history_years]

    # 2) helper to pull & clean a single row by its exact label
    def get_row_exact(label):
        if label not in df.index:
            # debug: show you exactly what's available
            raise KeyError(f"Row '{label}' not found; available rows are:\n{df.index.tolist()}")
        series = (
            df.loc[label]
              .infer_objects(copy=False)
              .fillna(0)
              .astype(float)
        )
        return series.tolist()[:history_years]

    # 3) populate each field
    isObj.revenue                 = scale_down_by_thousand(get_row_exact("Total Revenue"))
    isObj.costOfRevenue           = scale_down_by_thousand(get_row_exact("Cost Of Revenue"))
    isObj.grossProfit             = scale_down_by_thousand(get_row_exact("Gross Profit"))
    isObj.operatingIncome         = scale_down_by_thousand(get_row_exact("Operating Income"))
    isObj.netIncome               = scale_down_by_thousand(get_row_exact("Net Income"))
    isObj.researchAndDevelopment  = scale_down_by_thousand(get_row_exact("Research And Development"))
    isObj.ebitda                  = scale_down_by_thousand(get_row_exact("EBITDA"))
    isObj.interestExpense         = scale_down_by_thousand(get_row_exact("Interest Expense"))

    # (Optional) debug print
    print("dates:               ", isObj.dates)
    print("revenue:             ", isObj.revenue)
    print("costOfRevenue:       ", isObj.costOfRevenue)
    print("grossProfit:         ", isObj.grossProfit)
    print("operatingIncome:     ", isObj.operatingIncome)
    print("netIncome:           ", isObj.netIncome)
    print("researchAndDev:      ", isObj.researchAndDevelopment)
    print("ebitda:              ", isObj.ebitda)
    print("interestExpense:     ", isObj.interestExpense)

    return isObj


def readQuarterlyISDataWithYFinance(ticker, history_quarters=5):
    """
    Fetch quarterly income‐statement history for `ticker` via yfinance only.
    Populates ISObj with exactly these row labels from df.index:
      - Total Revenue
      - Cost Of Revenue
      - Gross Profit
      - Operating Income
      - Net Income
      - Research And Development
      - EBITDA
      - Interest Expense
    """
    isObj = ISObj(ticker)
    df    = yf.Ticker(ticker).quarterly_financials

    # 1) grab the up-to-N most recent quarter-ending dates
    isObj.dates = [c.strftime("%Y-%m-%d") for c in df.columns][:history_quarters]

    # 2) helper to pull & clean a single row by its exact label
    def get_row_exact(label):
        if label not in df.index:
            raise KeyError(
                f"Row '{label}' not found; available rows are:\n{df.index.tolist()}"
            )
        return (
            df.loc[label]
              .infer_objects(copy=False)
              .fillna(0)
              .astype(float)
              .tolist()[:history_quarters]
        )

    # 3) populate each field
    isObj.revenue                 = scale_down_by_thousand(get_row_exact("Total Revenue"))
    isObj.costOfRevenue           = scale_down_by_thousand(get_row_exact("Cost Of Revenue"))
    isObj.grossProfit             = scale_down_by_thousand(get_row_exact("Gross Profit"))
    isObj.operatingIncome         = scale_down_by_thousand(get_row_exact("Operating Income"))
    isObj.netIncome               = scale_down_by_thousand(get_row_exact("Net Income"))
    isObj.researchAndDevelopment  = scale_down_by_thousand(get_row_exact("Research And Development"))
    isObj.ebitda                  = scale_down_by_thousand(get_row_exact("EBITDA"))
    isObj.interestExpense         = scale_down_by_thousand(get_row_exact("Interest Expense"))

    # (Optional) debug print
    print("quarterly dates:           ", isObj.dates)
    print("quarterly revenue:         ", isObj.revenue)
    print("quarterly costOfRevenue:   ", isObj.costOfRevenue)
    print("quarterly grossProfit:     ", isObj.grossProfit)
    print("quarterly operatingIncome: ", isObj.operatingIncome)
    print("quarterly netIncome:       ", isObj.netIncome)
    print("quarterly researchAndDev:  ", isObj.researchAndDevelopment)
    print("quarterly ebitda:          ", isObj.ebitda)
    print("quarterly interestExpense: ", isObj.interestExpense)

    return isObj

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    quarterlyISObj = readQuarterlyISDataWithYFinance(args.ticker)
    annualISObj = readAnnualISDataWithYFinance(args.ticker)

 
