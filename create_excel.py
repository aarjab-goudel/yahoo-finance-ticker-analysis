from bs_obj import *
from cf_obj import *
from is_obj import *
from stock_obj import *
from future_stock_obj import *
import pandas as pd
import xlsxwriter
from bs4 import BeautifulSoup
import urllib.request as ur
import requests
from urllib.request import Request, urlopen
from datetime import datetime
import argparse
import time
print('Starting now -- please wait until finished')
parser = argparse.ArgumentParser(description='Enter tickers seperated by commas')
parser.add_argument('-t', '--ticker', dest='tickers', action='append', default=[], required=True, help='Enter tickers separated by commas')
args = parser.parse_args()


tickers = args.tickers[0].split(',')

annualBSObjs = []
annualISObjs = []
annualCFObjs = []
stockObjs = []
futureStockObjs = []

quarterlyBSObjs = []
quarterlyISObjs = []
quarterlyCFObjs = []


def findObjByTicker(objs, ticker):
    for obj in objs:
        searchTicker = obj.ticker
        if (searchTicker == ticker):
            return obj
    return None

def isCfObjValid(cfObj, year):
    try:
        cfObj.dates[year]
    except:
        cfObj.dates.append('0.000')
    
    try:
        cfObj.freeCashFlow[year]
    except:
        cfObj.freeCashFlow.append('0.000')
    
    try:
        cfObj.netCashByOperatingActivities[year]
    except:
        cfObj.netCashByOperatingActivities.append('0.000')

    try:
        cfObj.netCashForInvestingActivities[year]
    except:
        cfObj.netCashForInvestingActivities.append('0.000')

    try:
        cfObj.netCashForFinancingActivities[year]
    except:
        cfObj.netCashForFinancingActivities.append('0.000')

    try:
        cfObj.capitalExpenditures[year]
    except:
        cfObj.capitalExpenditures.append('0.000')

def isBsObjValid(bsObj, year):
    try:
        bsObj.dates[year]
    except:
        bsObj.dates.append('0.000')
    
    try:
        bsObj.totalAssets[year]
    except:
        bsObj.totalAssets.append('0.000')

    try:
        bsObj.totalLiabilities[year]
    except:
        bsObj.totalLiabilities.append('0.000')

    try:
        bsObj.totalEquity[year]
    except:
        bsObj.totalEquity.append('0.000')


    try:
        bsObj.totalCash
    except:
        bsObj.totalCash = '0.000'

    try:
        bsObj.totalDebt
    except:
        bsObj.totalDebt = '0.000'

    try:
        bsObj.currentRatio
    except:
        bsObj.currentRatio = '0.000'

    

def isIsObjValid(isObj, year):
    try:
        isObj.dates[year]
    except:
        isObj.dates.append('0.000')

    try:
        isObj.revenue[year]
    except:
        isObj.revenue.append('0.000')

    try:
        isObj.costOfRevenue[year]
    except:
        isObj.costOfRevenue.append('0.000')

    try:
        isObj.grossProfit[year]
    except:
        isObj.grossProfit.append('0.000')

    try:
        isObj.netIncome[year]
    except:
        isObj.netIncome.append('0.000')

    try:
        isObj.researchAndDevelopment[year]
    except:
        isObj.researchAndDevelopment.append('0.000')


def writeToCFSheet(cfSheet, cfObjs, stockObjs, tickers, year):
    cfSheetHeader = ['Stock', 'Ticker', 'Sector', 'Industry', 'Date', 'Currency Type', 'Free Cash Flow', 'Free Cash Flow Growth', 'Net cash provided by operating activities', 'Net cash rovided by operating activities growth', 'Net cash used for investing activities', 'Net cash provided by (used for) financing activities', 'Capital Expenditures', 'Ticker']
    row = 0
    column = 0
    for item in cfSheetHeader:
        cfSheet.write(row, column, item)
        column += 1
    row += 1
    column = 0
    for ticker in tickers:
        cfObj = findObjByTicker(cfObjs, ticker)
        isCfObjValid(cfObj, year)
        stockObj = findObjByTicker(stockObjs, ticker)
        cfSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, cfObj.dates[year], stockObj.currency, cfObj.freeCashFlow[year], '0.000', cfObj.netCashByOperatingActivities[year], '0.000', cfObj.netCashForInvestingActivities[year], cfObj.netCashForFinancingActivities[year], '0.000', stockObj.ticker]
        for content in cfSheetDataContent:
            cfSheet.write(row, column, content)
            column += 1
        column = 0
        row += 1

# Remove Earnings Per Share, Earnings Per Shares Growth
# 0 = Stock
# 1 = Ticker
# 2 = Sector
# 3 = Industry
# 4 = Date
# 5 = Currency
# 6 = Revenue
# 7 = Revenue Growth
# 8 = Cost of Revenue
# 9 = Cost of Revenue Growth
# 10 = Gross Profit
# 11 = Gross Profit Growth
# 12 = Net Income
# 13 = Net Income Growth
# 14 = Research And Development
# 15 = Research And Development Growth
# 16 = Ticker
def writeToISSheet(isSheet, isObjs, stockObjs, tickers, year):
    isSheetHeader = ['Stock', 'Ticker', 'Sector', 'Industry', 'Date', 'Currency Type', 'Revenue', 'Revenue Growth', 'Cost of Revenue', 'Cost of Revenue Growth', 'Gross Profit', 'Gross Profit Growth', 'Net Income', 'Net Income Growth', 'Research and Development', 'Research and Development Growth', 'Ticker']
    #isSheetHeader = ['Stock', 'Ticker', 'Sector', 'Industry', 'Date', 'Currency Type', 'Revenue', 'Revenue Growth', 'Cost of Revenue', 'Cost of Revenue Growth', 'Gross profit', 'Gross Profit Growth', 'Net Income', 'Net Income Growth', 'Earnings Per Share', 'Earnings Per Share Growth', 'Research and Development', 'Research and Development Growth', 'Ticker']
    row = 0
    column = 0
    for item in isSheetHeader:
        isSheet.write(row, column, item)
        column += 1
    row += 1
    column = 0
    for ticker in tickers:
        isObj = findObjByTicker(isObjs, ticker)
        isIsObjValid(isObj, year)
        stockObj = findObjByTicker(stockObjs, ticker)
        isSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, isObj.dates[year], stockObj.currency, isObj.revenue[year], '0.000', isObj.costOfRevenue[year], '0.000', isObj.grossProfit[year], '0.000', isObj.netIncome[year], '0.000', isObj.researchAndDevelopment[year], '0.000', stockObj.ticker]
        #isSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, isObj.dates[year], 'USD', isObj.revenue[year], '0.000', isObj.costOfRevenue[year], '0.000', isObj.grossProfit[year], '0.000', isObj.netIncome[year], '0.000', '0.000', '0.000', isObj.researchAndDevelopment[year], '0.000', stockObj.ticker]
        for content in isSheetDataContent:
            isSheet.write(row, column, content)
            column += 1
        column = 0
        row += 1

# Remove Net Equity, Net Equity Growth, Short Term Debt Long Term Debt, Net Intagible Assets, Tangible Assets, Recievables, and Accounts Payable.
# Add totalCash (Most Recent Quarter), total debt (Most Recent Quarter), current ratio (Most Recent Quarter)
# 0 = Stock
# 1 = Ticker
# 2 = Sector
# 3 = Industry
# 4 = Date
# 5 = Currency
# 6 = Total Equity
# 7 = Total Equity Growth
# 8 = Total Assets
# 9 = Total Liabilities
# 10 = Total Cash (mrq)
# 11 = Total Debt (mrq)
# 12 = Current Ratio (mrq)
# 13 = Ticker
def writeToBalanceSheet(bsSheet, bsObjs, stockObjs, tickers, year):
   # bsSheetHeader = ['Stock', 'Ticker', 'Sector', 'Industry', 'Date', 'Currency Type', 'Net Equity', 'Net Equity Growth', 'Total Shareholders Equity', 'Total Shareholders Equity Growth', 'Total intangible assets', 'Total Assets', 'Total Liabilities', 'Total Tangible Assets', 'Short Term Debt', 'Long Term Debt', 'Recievables', 'Accounts Payable', 'Ticker']
    bsSheetHeader = ['Stock', 'Ticker', 'Sector', 'Industry', 'Date', 'Currency Type', 'Total Shareholders Equity', 'Total Shareholders Equity Growth', 'Total Assets', 'Total Liabilities', 'Total Cash (Most Recent Quarter)', 'Total Debt (Most Recent Quarter)', 'Current Ratio (Most Recent Quarter)', 'Ticker']
    row = 0
    column = 0
    for item in bsSheetHeader:
        bsSheet.write(row, column, item)
        column += 1
    row += 1
    column = 0
    for ticker in tickers:
        bsObj = findObjByTicker(bsObjs, ticker)
        isBsObjValid(bsObj, year)
        stockObj = findObjByTicker(stockObjs, ticker)
        bsSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, bsObj.dates[year], stockObj.currency, bsObj.totalEquity[year], '0.000', bsObj.totalAssets[year], bsObj.totalLiabilities[year], bsObj.totalCash, bsObj.totalDebt, bsObj.currentRatio, stockObj.ticker ]
        #bsSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, bsObj.dates[year], 'USD', '0.000', '0.000', bsObj.totalEquity[year], '0.000', '0.000', bsObj.totalAssets[year], bsObj.totalLiabilities[year], bsObj.netTangibleAssets[year], bsObj.shortTermDebt[year], bsObj.longTermDebt[year], '0.000', '0.000', stockObj.ticker]
        for content in bsSheetDataContent:
            bsSheet.write(row, column, content)
            column += 1
        column = 0
        row += 1


def setUpAnnualAndQuarterlyObjects():
    for ticker in tickers:
        print(ticker)
        annualBSObj = readAnnualBSDataForTicker(ticker)
        annualBSObjs.append(annualBSObj)
        quarterlyBSObj = readQuarterlyBSDataForTicker(ticker)
        quarterlyBSObjs.append(quarterlyBSObj)

        print('FINISHED BALANCE SHEET')

        annualISObj = readAnnualISDataForTicker(ticker)
        annualISObjs.append(annualISObj)
        quarterlyISObj = readQuarterlyISDataForTicker(ticker)
        quarterlyISObjs.append(quarterlyISObj)

        print('FINISHED INCOME SHEET')

        annualCFObj = readAnnualCFDataForTicker(ticker)
        annualCFObjs.append(annualCFObj)
        quartleryCFObj = readQuarterlyCFDataForTicker(ticker)
        quarterlyCFObjs.append(quartleryCFObj)

        print('FINISHED CASH FLOW SHEET')

        stockObj = readCommonStockData(ticker)
        stockObjs.append(stockObj)

        futureStockObj = readFutureStockData(ticker)
        futureStockObjs.append(futureStockObj)

        print('FINISHED FUTURE STOCK DATA')
        time.sleep(10)
    


def createFutureExcelWorkbook():
    wb = xlsxwriter.Workbook('FutureStockData.xlsx')

    futureStockDataSheet = wb.add_worksheet('Future Stock Data')
    futureStockDataHeader = ['Ticker', 'Current Year', 'Current Year EPS', 'Current Year Revenue', 'Next Year', 'Next Year EPS', 'Next Year Revenue', 'EPS Growth', 'Revenue Growth']
    row = 0
    column = 0
    for item in futureStockDataHeader:
        futureStockDataSheet.write(row, column, item)
        column += 1
    row += 1
    column = 0
    for ticker in tickers:
        futureStockObj = findObjByTicker(futureStockObjs, ticker)
        futureStockContent = [ticker, futureStockObj.currentYear, futureStockObj.currentYearEPS, futureStockObj.currentYearRev, futureStockObj.nextYear, futureStockObj.nextYearEPS, futureStockObj.nextYearRev, '0.000', '0.000']
        for content in futureStockContent:
            futureStockDataSheet.write(row, column, content)
            column += 1
        column = 0
        row += 1
    
    wb.close()




def createQuarterlyExcelWorkbook():
    wb = xlsxwriter.Workbook('QuarterlyStockData.xlsx')

    bsSheetOne = wb.add_worksheet('BS')
    writeToBalanceSheet(bsSheetOne, quarterlyBSObjs, stockObjs, tickers, 0)
    bsSheetTwo = wb.add_worksheet('BSOne')
    writeToBalanceSheet(bsSheetTwo, quarterlyBSObjs, stockObjs, tickers, 1)
    bsSheetThree = wb.add_worksheet('BSTwo')
    writeToBalanceSheet(bsSheetThree, quarterlyBSObjs, stockObjs, tickers, 2)
    bsSheetFour = wb.add_worksheet('BSThree')
    writeToBalanceSheet(bsSheetFour, quarterlyBSObjs, stockObjs, tickers, 3)

    isSheetOne = wb.add_worksheet('IS')
    writeToISSheet(isSheetOne, quarterlyISObjs, stockObjs, tickers, 0)
    isSheetTwo = wb.add_worksheet('ISOne')
    writeToISSheet(isSheetTwo, quarterlyISObjs, stockObjs, tickers, 1)
    isSheetThree = wb.add_worksheet('ISTwo')
    writeToISSheet(isSheetThree, quarterlyISObjs, stockObjs, tickers, 2)
    isSheetFour = wb.add_worksheet('ISThree')
    writeToISSheet(isSheetFour, quarterlyISObjs, stockObjs, tickers, 3)

    cfSheetOne = wb.add_worksheet('CF')
    writeToCFSheet(cfSheetOne, quarterlyCFObjs, stockObjs, tickers, 0)
    cfSheetTwo = wb.add_worksheet('CFOne')
    writeToCFSheet(cfSheetTwo, quarterlyCFObjs, stockObjs, tickers, 1)
    cfSheetThree = wb.add_worksheet('CFTwo')
    writeToCFSheet(cfSheetThree, quarterlyCFObjs, stockObjs, tickers, 2)
    cfSheetFour = wb.add_worksheet('CFThree')
    writeToCFSheet(cfSheetFour, quarterlyCFObjs, stockObjs, tickers, 3)

    wb.close()




def createAnnualExcelWorkbook():
    wb = xlsxwriter.Workbook('AnnualStockData.xlsx')

    stockSheet = wb.add_worksheet('Stock Data')
    stockSheetHeaderContent = ['Stock', 'Ticker', 'Sector', 'Industry', 'Annual Dividend Percent Yield', 'Average 5 Year Dividend Yield', 'Current P/B Ratio', 'Average 5 Year P/B ratio', 'Current P/E ratio', 'Average 5 Year P/E ratio', 'Forward P/E Ratio', 'PEG Ratio', 'Average Current Ratio', 'Average Debt to Equity Ratio', 'Ticker']
    row = 0
    column = 0
    for item in stockSheetHeaderContent:
        stockSheet.write(row, column, item)
        column += 1
    row += 1
    column = 0
    for ticker in tickers:
        stockObj = findObjByTicker(stockObjs, ticker)
        stockSheetDataContent = [stockObj.fullName, stockObj.ticker, stockObj.sector, stockObj.industry, stockObj.dividend, '-', '-', '-', stockObj.peRatio, '-', '-', '-', '-', '-', stockObj.ticker]
        for stockItem in stockSheetDataContent:
            stockSheet.write(row, column, stockItem)
            column += 1
        column = 0
        row += 1

    bsSheetOne = wb.add_worksheet('BS')
    writeToBalanceSheet(bsSheetOne, annualBSObjs, stockObjs, tickers, 0)
    bsSheetTwo = wb.add_worksheet('BSOne')
    writeToBalanceSheet(bsSheetTwo, annualBSObjs, stockObjs, tickers, 1)
    bsSheetThree = wb.add_worksheet('BSTwo')
    writeToBalanceSheet(bsSheetThree, annualBSObjs, stockObjs, tickers, 2)
    bsSheetFour = wb.add_worksheet('BSThree')
    writeToBalanceSheet(bsSheetFour, annualBSObjs, stockObjs, tickers, 3)
    
    isSheetOne = wb.add_worksheet('IS')
    writeToISSheet(isSheetOne, annualISObjs, stockObjs, tickers, 0)
    isSheetTwo = wb.add_worksheet('ISOne')
    writeToISSheet(isSheetTwo, annualISObjs, stockObjs, tickers, 1)
    isSheetThree = wb.add_worksheet('ISTwo')
    writeToISSheet(isSheetThree, annualISObjs, stockObjs, tickers, 2)
    isSheetFour = wb.add_worksheet('ISThree')
    writeToISSheet(isSheetFour, annualISObjs, stockObjs, tickers, 3)

    cfSheetOne = wb.add_worksheet('CF')
    writeToCFSheet(cfSheetOne, annualCFObjs, stockObjs, tickers, 0)
    cfSheetTwo = wb.add_worksheet('CFOne')
    writeToCFSheet(cfSheetTwo, annualCFObjs, stockObjs, tickers, 1)
    cfSheetThree = wb.add_worksheet('CFTwo')
    writeToCFSheet(cfSheetThree, annualCFObjs, stockObjs, tickers, 2)
    cfSheetFour = wb.add_worksheet('CFThree')
    writeToCFSheet(cfSheetFour, annualCFObjs, stockObjs, tickers, 3)

    wb.close()

setUpAnnualAndQuarterlyObjects()
createAnnualExcelWorkbook()
createQuarterlyExcelWorkbook()
createFutureExcelWorkbook()

print('Finished!')