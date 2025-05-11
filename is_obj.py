#!/usr/bin/env python3
import time
import math
from common_service import *
from bs4 import BeautifulSoup
import requests

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


if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    isObj = readAnnualISDataForTicker(args.ticker)
 
