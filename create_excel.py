#!/usr/bin/env python3
from bs_obj import *
from cf_obj import *
from is_obj import *
from stock_obj import *
from future_stock_obj import *
import xlsxwriter
from bs4 import BeautifulSoup
import urllib.request as ur
import requests
from urllib.request import Request, urlopen
from datetime import datetime
import argparse
import time
from pathlib import Path
import os
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

annual_ticker_map = None
quarterly_ticker_map = None



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
    open_browser()
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
    close_browser()
    


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

def setUpQuarterlyTickerMap():
    ticker_map = {}
    for ticker in tickers:
        ticker_map[ticker] = []
        for quarterlyBSObj in quarterlyBSObjs:
            bsObjTicker = quarterlyBSObj.ticker
            if bsObjTicker == ticker:
                ticker_map[ticker].append(quarterlyBSObj)
        
        for quarterlyISObj in quarterlyISObjs:
            isObjTicker = quarterlyISObj.ticker
            if isObjTicker == ticker:
                ticker_map[ticker].append(quarterlyISObj)

        for quarterlyCFObj in quarterlyCFObjs:
            cfObjTicker = quarterlyCFObj.ticker
            if cfObjTicker == ticker:
                ticker_map[ticker].append(quarterlyCFObj)

    return ticker_map

def setUpAnnualTickerMap():  
    
    ticker_map = {}
    for ticker in tickers:
        ticker_map[ticker] = []
        for annualBSObj in annualBSObjs:
            bsObjTicker = annualBSObj.ticker
            if annualBSObj.ticker == ticker:
                ticker_map[ticker].append(annualBSObj)

        for annualISObj in annualISObjs:
            isObjTicker = annualISObj.ticker
            if annualISObj.ticker == ticker:
                ticker_map[ticker].append(annualISObj)

        for annualCFObj in annualCFObjs:
            cfObjTicker = annualCFObj.ticker
            if annualCFObj.ticker == ticker:
                ticker_map[ticker].append(annualCFObj)

        for stockObj in stockObjs:
            stockObjTicker = stockObj.ticker
            if stockObj.ticker == ticker:
                ticker_map[ticker].append(stockObj)

        for futureStockObj in futureStockObjs:
            futureStockTicker = futureStockObj.ticker
            if futureStockObj.ticker == ticker:
                ticker_map[ticker].append(futureStockObj)

    return ticker_map

def createQuarterlyStockTxtFile(ticker, base_dir):
    p = Path(ticker)
    ticker_dir = base_dir / ticker
    txt_path = ticker_dir / f"{ticker}.txt"
    quarterlyBSObj = quarterly_ticker_map[ticker][0]
    quarterlyISObj = quarterly_ticker_map[ticker][1]
    quarterlyCFObj = quarterly_ticker_map[ticker][2]
    stockObj = annual_ticker_map[ticker][3]
    futureStockObj = annual_ticker_map[ticker][4]
    annualBSObj = annual_ticker_map[ticker][0]
    with open(txt_path, "w") as f:
        f.write(f"===================================================== {ticker} (Currency in {stockObj.currency}) - Balance Sheet =====================================================  ")
        f.write("\n"f"                                         {quarterlyBSObj.dates[4]}             {quarterlyBSObj.dates[3]}             {quarterlyBSObj.dates[2]}             {quarterlyBSObj.dates[1]}             {quarterlyBSObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Assets                             {removeDecimalFromStr(quarterlyBSObj.totalAssets[4])}            {removeDecimalFromStr(quarterlyBSObj.totalAssets[3])}            {removeDecimalFromStr(quarterlyBSObj.totalAssets[2])}            {removeDecimalFromStr(quarterlyBSObj.totalAssets[1])}             {removeDecimalFromStr(quarterlyBSObj.totalAssets[0])}")
        f.write("\n"f"Total Assets Growth                                {percent_change(quarterlyBSObj.totalAssets[4], quarterlyBSObj.totalAssets[3])}                 {percent_change(quarterlyBSObj.totalAssets[3], quarterlyBSObj.totalAssets[2])}                 {percent_change(quarterlyBSObj.totalAssets[2], quarterlyBSObj.totalAssets[1])}                 {percent_change(quarterlyBSObj.totalAssets[1], quarterlyBSObj.totalAssets[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Liabilities                        {removeDecimalFromStr(quarterlyBSObj.totalLiabilities[4])}            {removeDecimalFromStr(quarterlyBSObj.totalLiabilities[3])}            {removeDecimalFromStr(quarterlyBSObj.totalLiabilities[2])}            {removeDecimalFromStr(quarterlyBSObj.totalLiabilities[1])}            {removeDecimalFromStr(quarterlyBSObj.totalLiabilities[0])}")
        f.write("\n"f"Total Liabilities Growth                           {percent_change(quarterlyBSObj.totalLiabilities[4], quarterlyBSObj.totalLiabilities[3])}                 {percent_change(quarterlyBSObj.totalLiabilities[3], quarterlyBSObj.totalLiabilities[2])}                 {percent_change(quarterlyBSObj.totalLiabilities[2], quarterlyBSObj.totalLiabilities[1])}                 {percent_change(quarterlyBSObj.totalLiabilities[1], quarterlyBSObj.totalLiabilities[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Shareholders Equity                {removeDecimalFromStr(quarterlyBSObj.totalEquity[4])}             {removeDecimalFromStr(quarterlyBSObj.totalEquity[3])}             {removeDecimalFromStr(quarterlyBSObj.totalEquity[2])}             {removeDecimalFromStr(quarterlyBSObj.totalEquity[1])}             {removeDecimalFromStr(quarterlyBSObj.totalEquity[0])}")
        f.write("\n"f"Total Shareholders Equity Growth                   {percent_change(quarterlyBSObj.totalEquity[4], quarterlyBSObj.totalEquity[3])}                {percent_change(quarterlyBSObj.totalEquity[3], quarterlyBSObj.totalEquity[2])}                {percent_change(quarterlyBSObj.totalEquity[2], quarterlyBSObj.totalEquity[1])}                {percent_change(quarterlyBSObj.totalEquity[1], quarterlyBSObj.totalEquity[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Cash (Most Recent Quarter)         ${annualBSObj.totalCash}")
        f.write("\n"f"Total Debt (Most Recent Quarter)         ${annualBSObj.totalDebt}")
        f.write("\n"f"Current Ratio (Most Recent Quarter)      {annualBSObj.currentRatio}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Balance Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Income Sheet =====================================================  ")
        f.write("\n"f"                                         {quarterlyISObj.dates[4]}             {quarterlyISObj.dates[3]}             {quarterlyISObj.dates[2]}             {quarterlyISObj.dates[1]}             {quarterlyISObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Revenue                                  {removeDecimalFromStr(quarterlyISObj.revenue[4])}            {removeDecimalFromStr(quarterlyISObj.revenue[3])}            {removeDecimalFromStr(quarterlyISObj.revenue[2])}            {removeDecimalFromStr(quarterlyISObj.revenue[1])}            {removeDecimalFromStr(quarterlyISObj.revenue[0])}")
        f.write("\n"f"Revenue Growth                                     {percent_change(quarterlyISObj.revenue[4], quarterlyISObj.revenue[3])}                 {percent_change(quarterlyISObj.revenue[3], quarterlyISObj.revenue[2])}                 {percent_change(quarterlyISObj.revenue[2], quarterlyISObj.revenue[1])}                 {percent_change(quarterlyISObj.revenue[1], quarterlyISObj.revenue[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Gross Profit                             {removeDecimalFromStr(quarterlyISObj.grossProfit[4])}            {removeDecimalFromStr(quarterlyISObj.grossProfit[3])}            {removeDecimalFromStr(quarterlyISObj.grossProfit[2])}            {removeDecimalFromStr(quarterlyISObj.grossProfit[1])}            {removeDecimalFromStr(quarterlyISObj.grossProfit[0])}")
        f.write("\n"f"Gross Profit Growth                                {percent_change(quarterlyISObj.grossProfit[4], quarterlyISObj.grossProfit[3])}                {percent_change(quarterlyISObj.grossProfit[3], quarterlyISObj.grossProfit[2])}                 {percent_change(quarterlyISObj.grossProfit[2], quarterlyISObj.grossProfit[1])}                 {percent_change(quarterlyISObj.grossProfit[1], quarterlyISObj.grossProfit[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Net Income                               {removeDecimalFromStr(quarterlyISObj.netIncome[4])}             {removeDecimalFromStr(quarterlyISObj.netIncome[3])}             {removeDecimalFromStr(quarterlyISObj.netIncome[2])}             {removeDecimalFromStr(quarterlyISObj.netIncome[1])}             {removeDecimalFromStr(quarterlyISObj.netIncome[0])}")
        f.write("\n"f"Net Income Growth                                  {percent_change(quarterlyISObj.netIncome[4], quarterlyISObj.netIncome[3])}                 {percent_change(quarterlyISObj.netIncome[3], quarterlyISObj.netIncome[2])}                 {percent_change(quarterlyISObj.netIncome[2], quarterlyISObj.netIncome[1])}                 {percent_change(quarterlyISObj.netIncome[1], quarterlyISObj.netIncome[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Research And Development                 {removeDecimalFromStr(quarterlyISObj.researchAndDevelopment[4])}             {removeDecimalFromStr(quarterlyISObj.researchAndDevelopment[3])}             {removeDecimalFromStr(quarterlyISObj.researchAndDevelopment[2])}             {quarterlyISObj.researchAndDevelopment[1]}            {quarterlyISObj.researchAndDevelopment[0]}")
        f.write("\n"f"Research And Development Growth                    {percent_change(quarterlyISObj.researchAndDevelopment[4], quarterlyISObj.researchAndDevelopment[3])}                {percent_change(quarterlyISObj.researchAndDevelopment[3], quarterlyISObj.researchAndDevelopment[2])}                {percent_change(quarterlyISObj.researchAndDevelopment[2], quarterlyISObj.researchAndDevelopment[1])}                {percent_change(quarterlyISObj.researchAndDevelopment[1], quarterlyISObj.researchAndDevelopment[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EBITDA                                  {removeDecimalFromStr(quarterlyISObj.ebitda[4])}            {removeDecimalFromStr(quarterlyISObj.ebitda[3])}            {removeDecimalFromStr(quarterlyISObj.ebitda[2])}            {removeDecimalFromStr(quarterlyISObj.ebitda[1])}            {removeDecimalFromStr(quarterlyISObj.ebitda[0])}")
        f.write("\n"f"EBITDA Growth                                     {percent_change(quarterlyISObj.ebitda[4], quarterlyISObj.ebitda[3])}                 {percent_change(quarterlyISObj.ebitda[3], quarterlyISObj.ebitda[2])}                 {percent_change(quarterlyISObj.ebitda[2], quarterlyISObj.ebitda[1])}                 {percent_change(quarterlyISObj.ebitda[1], quarterlyISObj.ebitda[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Income Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Cash Flow Sheet =====================================================  ")
        f.write("\n"f"                                         {quarterlyCFObj.dates[4]}             {quarterlyCFObj.dates[3]}             {quarterlyCFObj.dates[2]}             {quarterlyCFObj.dates[1]}             {quarterlyCFObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Free Cash Flow                           {removeDecimalFromStr(quarterlyCFObj.freeCashFlow[4])}             {removeDecimalFromStr(quarterlyCFObj.freeCashFlow[3])}            {removeDecimalFromStr(quarterlyCFObj.freeCashFlow[2])}             {removeDecimalFromStr(quarterlyCFObj.freeCashFlow[1])}             {removeDecimalFromStr(quarterlyCFObj.freeCashFlow[0])}")
        f.write("\n"f"Free Cash Flow Growth                              {percent_change(quarterlyCFObj.freeCashFlow[4], quarterlyCFObj.freeCashFlow[3])}                {percent_change(quarterlyCFObj.freeCashFlow[3], quarterlyCFObj.freeCashFlow[2])}                {percent_change(quarterlyCFObj.freeCashFlow[2], quarterlyCFObj.freeCashFlow[1])}                {percent_change(quarterlyCFObj.freeCashFlow[1], quarterlyCFObj.freeCashFlow[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Net Cash For Investing                   {removeDecimalFromStr(quarterlyCFObj.netCashForInvestingActivities[4])}            {removeDecimalFromStr(quarterlyCFObj.netCashForInvestingActivities[3])}            {removeDecimalFromStr(quarterlyCFObj.netCashForInvestingActivities[2])}              {removeDecimalFromStr(quarterlyCFObj.netCashForInvestingActivities[1])}              {removeDecimalFromStr(quarterlyCFObj.netCashForInvestingActivities[0])}")
        f.write("\n"f"Net Cash For Financing                   {removeDecimalFromStr(quarterlyCFObj.netCashForFinancingActivities[4])}            {removeDecimalFromStr(quarterlyCFObj.netCashForFinancingActivities[3])}           {removeDecimalFromStr(quarterlyCFObj.netCashForFinancingActivities[2])}           {removeDecimalFromStr(quarterlyCFObj.netCashForFinancingActivities[1])}           {removeDecimalFromStr(quarterlyCFObj.netCashForFinancingActivities[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Cash Flow Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Multiples ===============================================================")
        f.write("\n"f"                                         {annualBSObj.ev_ebitda_dates[5]}             {annualBSObj.ev_ebitda_dates[4]}             {annualBSObj.ev_ebitda_dates[3]}             {annualBSObj.ev_ebitda_dates[2]}             {annualBSObj.ev_ebitda_dates[1]}             {annualBSObj.ev_ebitda_dates[0]}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EV/EBITDA                                 {annualBSObj.ev_ebitda[5]}                 {annualBSObj.ev_ebitda[4]}                 {annualBSObj.ev_ebitda[3]}                 {annualBSObj.ev_ebitda[2]}                 {annualBSObj.ev_ebitda[1]}                 {annualBSObj.ev_ebitda[0]}")
        f.write("\n"f"EV/EBITDA Growth                              {percent_change(annualBSObj.ev_ebitda[5], annualBSObj.ev_ebitda[4])}                 {percent_change(annualBSObj.ev_ebitda[4], annualBSObj.ev_ebitda[3])}                 {percent_change(annualBSObj.ev_ebitda[3], annualBSObj.ev_ebitda[2])}                 {percent_change(annualBSObj.ev_ebitda[2], annualBSObj.ev_ebitda[1])}                 {percent_change(annualBSObj.ev_ebitda[1], annualBSObj.ev_ebitda[0])}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"PEG Ratio                                  {annualBSObj.peg_ratios[5]}                 {annualBSObj.peg_ratios[4]}                   {annualBSObj.peg_ratios[3]}                  {annualBSObj.peg_ratios[2]}                  {annualBSObj.peg_ratios[1]}                  {annualBSObj.peg_ratios[0]}")
        f.write("\n"f"PEG Ratio Growth                                {percent_change(annualBSObj.peg_ratios[5], annualBSObj.peg_ratios[4])}                     {percent_change(annualBSObj.peg_ratios[4], annualBSObj.peg_ratios[3])}                   {percent_change(annualBSObj.peg_ratios[3], annualBSObj.peg_ratios[2])}                {percent_change(annualBSObj.peg_ratios[2], annualBSObj.peg_ratios[1])}               {percent_change(annualBSObj.peg_ratios[1], annualBSObj.peg_ratios[0])}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Multiples ===============================================================")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - EBITDA/Interest Payments ===============================================================")
        f.write("\n"f"                                         {quarterlyISObj.dates[4]}             {quarterlyISObj.dates[3]}             {quarterlyISObj.dates[2]}             {quarterlyISObj.dates[1]}             {quarterlyISObj.dates[0]}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EBITDA/Interest Payments                  {calculateEBITDAInterst(quarterlyISObj.ebitda[4], quarterlyISObj.interestExpense[4])}                  {calculateEBITDAInterst(quarterlyISObj.ebitda[3], quarterlyISObj.interestExpense[3])}                 {calculateEBITDAInterst(quarterlyISObj.ebitda[2], quarterlyISObj.interestExpense[2])}                 {calculateEBITDAInterst(quarterlyISObj.ebitda[1], quarterlyISObj.interestExpense[1])}                 {calculateEBITDAInterst(quarterlyISObj.ebitda[1], quarterlyISObj.interestExpense[0])}")
        f.write("\n"f"EBITDA/Interest Payments Growth                    {percent_change(calculateEBITDAInterst(quarterlyISObj.ebitda[4], quarterlyISObj.interestExpense[4]), calculateEBITDAInterst(quarterlyISObj.ebitda[3], quarterlyISObj.interestExpense[3]))}                {percent_change(calculateEBITDAInterst(quarterlyISObj.ebitda[3], quarterlyISObj.interestExpense[3]), calculateEBITDAInterst(quarterlyISObj.ebitda[2], quarterlyISObj.interestExpense[2]))}                {percent_change(calculateEBITDAInterst(quarterlyISObj.ebitda[2], quarterlyISObj.interestExpense[2]), calculateEBITDAInterst(quarterlyISObj.ebitda[1], quarterlyISObj.interestExpense[1]))}                {percent_change(calculateEBITDAInterst(quarterlyISObj.ebitda[1], quarterlyISObj.interestExpense[1]), calculateEBITDAInterst(quarterlyISObj.ebitda[0], quarterlyISObj.interestExpense[0]))}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - EBITDA/Interest Payments ===============================================================")
        f.write("\n")
        f.write("\n")


def createAnnualStockTxtFile(ticker, base_dir):
    p = Path(ticker)
    ticker_dir = base_dir / ticker
    txt_path = ticker_dir / f"{ticker}.txt"
    annualBSObj = annual_ticker_map[ticker][0]
    annualISObj = annual_ticker_map[ticker][1]
    annualCFObj = annual_ticker_map[ticker][2]
    stockObj = annual_ticker_map[ticker][3]
    futureStockObj = annual_ticker_map[ticker][4]
    with open(txt_path, "w") as f:
        f.write(f"===================================================== {ticker} (Currency in {stockObj.currency}) - Balance Sheet =====================================================  ")
        f.write("\n"f"                                         {annualBSObj.dates[3]}             {annualBSObj.dates[2]}             {annualBSObj.dates[1]}             {annualBSObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Assets                             {removeDecimalFromStr(annualBSObj.totalAssets[3])}            {removeDecimalFromStr(annualBSObj.totalAssets[2])}            {removeDecimalFromStr(annualBSObj.totalAssets[1])}            {removeDecimalFromStr(annualBSObj.totalAssets[0])}")
        f.write("\n"f"Total Assets Growth                                {percent_change(annualBSObj.totalAssets[3], annualBSObj.totalAssets[2])}                 {percent_change(annualBSObj.totalAssets[2], annualBSObj.totalAssets[1])}                 {percent_change(annualBSObj.totalAssets[1], annualBSObj.totalAssets[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Liabilities                        {removeDecimalFromStr(annualBSObj.totalLiabilities[3])}            {removeDecimalFromStr(annualBSObj.totalLiabilities[2])}            {removeDecimalFromStr(annualBSObj.totalLiabilities[1])}            {removeDecimalFromStr(annualBSObj.totalLiabilities[0])}")
        f.write("\n"f"Total Liabilities Growth                           {percent_change(annualBSObj.totalLiabilities[3], annualBSObj.totalLiabilities[2])}                 {percent_change(annualBSObj.totalLiabilities[2], annualBSObj.totalLiabilities[1])}                 {percent_change(annualBSObj.totalLiabilities[1], annualBSObj.totalLiabilities[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Shareholders Equity                {removeDecimalFromStr(annualBSObj.totalEquity[3])}             {removeDecimalFromStr(annualBSObj.totalEquity[2])}             {removeDecimalFromStr(annualBSObj.totalEquity[1])}             {removeDecimalFromStr(annualBSObj.totalEquity[0])}")
        f.write("\n"f"Total Shareholders Equity Growth                   {percent_change(annualBSObj.totalEquity[3], annualBSObj.totalEquity[2])}                {percent_change(annualBSObj.totalEquity[2], annualBSObj.totalEquity[1])}                {percent_change(annualBSObj.totalEquity[1], annualBSObj.totalEquity[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Total Cash (Most Recent Quarter)         ${annualBSObj.totalCash}")
        f.write("\n"f"Total Debt (Most Recent Quarter)         ${annualBSObj.totalDebt}")
        f.write("\n"f"Current Ratio (Most Recent Quarter)      {annualBSObj.currentRatio}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Balance Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Income Sheet =====================================================  ")
        f.write("\n"f"                                         {annualISObj.dates[3]}             {annualISObj.dates[2]}             {annualISObj.dates[1]}             {annualISObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Revenue                                  {removeDecimalFromStr(annualISObj.revenue[3])}            {removeDecimalFromStr(annualISObj.revenue[2])}            {removeDecimalFromStr(annualISObj.revenue[1])}            {removeDecimalFromStr(annualISObj.revenue[0])}")
        f.write("\n"f"Revenue Growth                                     {percent_change(annualISObj.revenue[3], annualISObj.revenue[2])}                 {percent_change(annualISObj.revenue[2], annualISObj.revenue[1])}                 {percent_change(annualISObj.revenue[1], annualISObj.revenue[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Gross Profit                             {removeDecimalFromStr(annualISObj.grossProfit[3])}            {removeDecimalFromStr(annualISObj.grossProfit[2])}            {removeDecimalFromStr(annualISObj.grossProfit[1])}            {removeDecimalFromStr(annualISObj.grossProfit[0])}")
        f.write("\n"f"Gross Profit Growth                                {percent_change(annualISObj.grossProfit[3], annualISObj.grossProfit[2])}                {percent_change(annualISObj.grossProfit[2], annualISObj.grossProfit[1])}                 {percent_change(annualISObj.grossProfit[1], annualISObj.grossProfit[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Net Income                               {removeDecimalFromStr(annualISObj.netIncome[3])}             {removeDecimalFromStr(annualISObj.netIncome[2])}             {removeDecimalFromStr(annualISObj.netIncome[1])}             {removeDecimalFromStr(annualISObj.netIncome[0])}")
        f.write("\n"f"Net Income Growth                                  {percent_change(annualISObj.netIncome[3], annualISObj.netIncome[2])}                 {percent_change(annualISObj.netIncome[2], annualISObj.netIncome[1])}                 {percent_change(annualISObj.netIncome[1], annualISObj.netIncome[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Research And Development                 {removeDecimalFromStr(annualISObj.researchAndDevelopment[3])}             {removeDecimalFromStr(annualISObj.researchAndDevelopment[2])}             {removeDecimalFromStr(annualISObj.researchAndDevelopment[1])}             {annualISObj.researchAndDevelopment[0]}")
        f.write("\n"f"Research And Development Growth                    {percent_change(annualISObj.researchAndDevelopment[3], annualISObj.researchAndDevelopment[2])}                {percent_change(annualISObj.researchAndDevelopment[2], annualISObj.researchAndDevelopment[1])}                {percent_change(annualISObj.researchAndDevelopment[1], annualISObj.researchAndDevelopment[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EBITDA                                  {removeDecimalFromStr(annualISObj.ebitda[3])}            {removeDecimalFromStr(annualISObj.ebitda[2])}            {removeDecimalFromStr(annualISObj.ebitda[1])}            {removeDecimalFromStr(annualISObj.ebitda[0])}")
        f.write("\n"f"EBITDA Growth                                     {percent_change(annualISObj.ebitda[3], annualISObj.ebitda[2])}                 {percent_change(annualISObj.ebitda[2], annualISObj.ebitda[1])}                 {percent_change(annualISObj.ebitda[1], annualISObj.ebitda[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Income Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Cash Flow Sheet =====================================================  ")
        f.write("\n"f"                                         {annualCFObj.dates[3]}             {annualCFObj.dates[2]}             {annualCFObj.dates[1]}             {annualCFObj.dates[0]}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Free Cash Flow                           {removeDecimalFromStr(annualCFObj.freeCashFlow[3])}             {removeDecimalFromStr(annualCFObj.freeCashFlow[2])}            {removeDecimalFromStr(annualCFObj.freeCashFlow[1])}             {removeDecimalFromStr(annualCFObj.freeCashFlow[0])}")
        f.write("\n"f"Free Cash Flow Growth                              {percent_change(annualCFObj.freeCashFlow[3], annualCFObj.freeCashFlow[2])}                {percent_change(annualCFObj.freeCashFlow[2], annualCFObj.freeCashFlow[1])}                {percent_change(annualCFObj.freeCashFlow[1], annualCFObj.freeCashFlow[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Net Cash For Investing                   {removeDecimalFromStr(annualCFObj.netCashForInvestingActivities[3])}            {removeDecimalFromStr(annualCFObj.netCashForInvestingActivities[2])}            {removeDecimalFromStr(annualCFObj.netCashForInvestingActivities[1])}              {removeDecimalFromStr(annualCFObj.netCashForInvestingActivities[0])}")
        f.write("\n"f"Net Cash For Financing                   {removeDecimalFromStr(annualCFObj.netCashForFinancingActivities[3])}            {removeDecimalFromStr(annualCFObj.netCashForFinancingActivities[2])}           {removeDecimalFromStr(annualCFObj.netCashForFinancingActivities[1])}           {removeDecimalFromStr(annualCFObj.netCashForFinancingActivities[0])}")
        f.write("\n"f"---------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Cash Flow Sheet =====================================================  ")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Future Data Analysis for EPS")
        f.write("\n"f"For Current Year ({futureStockObj.currentYear}): The EPS is expected to be {futureStockObj.currentYearEPS}")
        f.write("\n"f"For Next Year ({futureStockObj.nextYear}): The EPS is expected to be {futureStockObj.nextYearEPS}")
        f.write("\n"f"The EPS Growth from Current Year ({futureStockObj.currentYear}) to Next Year ({futureStockObj.nextYear}) is {percent_change(futureStockObj.currentYearEPS, futureStockObj.nextYearEPS)}")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Future Data Analysis For Revenue")
        f.write("\n"f"For Current Year ({futureStockObj.currentYear}): The Revenue is expected to be {futureStockObj.currentYearRev}")
        f.write("\n"f"For Next Year ({futureStockObj.nextYear}): The Revenue is expected to be {futureStockObj.nextYearRev}")
        f.write("\n"f"The Revenue Growth from Current Year ({futureStockObj.currentYear}) to Next Year ({futureStockObj.nextYear}) is {percent_change(stripAlphabetFromNum(futureStockObj.currentYearRev), stripAlphabetFromNum(futureStockObj.nextYearRev))}")
        f.write("\n"f"==========================================================================================================================")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Multiples ===============================================================")
        f.write("\n"f"                                         {annualBSObj.ev_ebitda_dates[5]}             {annualBSObj.ev_ebitda_dates[4]}             {annualBSObj.ev_ebitda_dates[3]}             {annualBSObj.ev_ebitda_dates[2]}             {annualBSObj.ev_ebitda_dates[1]}             {annualBSObj.ev_ebitda_dates[0]}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EV/EBITDA                                 {annualBSObj.ev_ebitda[5]}                 {annualBSObj.ev_ebitda[4]}                 {annualBSObj.ev_ebitda[3]}                 {annualBSObj.ev_ebitda[2]}                 {annualBSObj.ev_ebitda[1]}                 {annualBSObj.ev_ebitda[0]}")
        f.write("\n"f"EV/EBITDA Growth                              {percent_change(annualBSObj.ev_ebitda[5], annualBSObj.ev_ebitda[4])}                 {percent_change(annualBSObj.ev_ebitda[4], annualBSObj.ev_ebitda[3])}                 {percent_change(annualBSObj.ev_ebitda[3], annualBSObj.ev_ebitda[2])}                 {percent_change(annualBSObj.ev_ebitda[2], annualBSObj.ev_ebitda[1])}                 {percent_change(annualBSObj.ev_ebitda[1], annualBSObj.ev_ebitda[0])}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"PEG Ratio                                  {annualBSObj.peg_ratios[5]}                 {annualBSObj.peg_ratios[4]}                   {annualBSObj.peg_ratios[3]}                  {annualBSObj.peg_ratios[2]}                  {annualBSObj.peg_ratios[1]}                  {annualBSObj.peg_ratios[0]}")
        f.write("\n"f"PEG Ratio Growth                                {percent_change(annualBSObj.peg_ratios[5], annualBSObj.peg_ratios[4])}                     {percent_change(annualBSObj.peg_ratios[4], annualBSObj.peg_ratios[3])}                   {percent_change(annualBSObj.peg_ratios[3], annualBSObj.peg_ratios[2])}                {percent_change(annualBSObj.peg_ratios[2], annualBSObj.peg_ratios[1])}               {percent_change(annualBSObj.peg_ratios[1], annualBSObj.peg_ratios[0])}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - Multiples ===============================================================")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - EBITDA/Interest Payments ===============================================================")
        f.write("\n"f"                                         {annualISObj.dates[3]}             {annualISObj.dates[2]}             {annualISObj.dates[1]}             {annualISObj.dates[0]}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"EBITDA/Interest Payments                  {calculateEBITDAInterst(annualISObj.ebitda[3], annualISObj.interestExpense[3])}                  {calculateEBITDAInterst(annualISObj.ebitda[2], annualISObj.interestExpense[2])}                 {calculateEBITDAInterst(annualISObj.ebitda[1], annualISObj.interestExpense[1])}                 {calculateEBITDAInterst(annualISObj.ebitda[0], annualISObj.interestExpense[0])}")
        f.write("\n"f"EBITDA/Interest Payments Growth                    {percent_change(calculateEBITDAInterst(annualISObj.ebitda[3], annualISObj.interestExpense[3]), calculateEBITDAInterst(annualISObj.ebitda[2], annualISObj.interestExpense[2]))}                {percent_change(calculateEBITDAInterst(annualISObj.ebitda[2], annualISObj.interestExpense[2]), calculateEBITDAInterst(annualISObj.ebitda[1], annualISObj.interestExpense[1]))}                {percent_change(calculateEBITDAInterst(annualISObj.ebitda[1], annualISObj.interestExpense[1]), calculateEBITDAInterst(annualISObj.ebitda[0], annualISObj.interestExpense[0]))}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} (Currency in {stockObj.currency}) - EBITDA/Interest Payments ===============================================================")
        f.write("\n")
        f.write("\n")
        f.write("\n"f"===================================================== {ticker} Dividend Yield and Current P/E Ratio ==================================================================")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"Dividend Yield: {stockObj.dividend}")
        f.write("\n"f"P/E Ratio: {stockObj.peRatio}")
        f.write("\n"f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        f.write("\n"f"===================================================== {ticker} Dividend Yield and Current P/E Ratio ==================================================================")
        f.write("\n")
        f.write("\n")


        
def setUpDirectories(dirName, tickers):
    """
    Creates a new folder named "<dirName>-<timestamp>" in the
    same directory as create_excel.py, then creates subfolders
    for each ticker. Returns the full Path.
    """

    # 1) Identify the directory where create_excel.py lives
    #    This ensures Annual/Quarterly folders go *alongside* create_excel.py.
    current_script_dir = Path(__file__).parent.resolve()

    # 2) Build the new folder name: e.g. "Annual-1673365582"
    timestamp = int(time.time())
    new_dir_name = f"{dirName}-{timestamp}"

    # 3) Combine them to get the full path
    #    e.g. /.../yahoo-finance-ticker-analysis/Annual-1673365582
    full_dir_path = current_script_dir / new_dir_name
    full_dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {full_dir_path}")

    # 4) Create a subfolder for each ticker
    for ticker in tickers:
        ticker_subdir = full_dir_path / ticker
        ticker_subdir.mkdir(exist_ok=True)
        print(f"Created subdirectory: {ticker_subdir}")

    # 5) Return the folder path
    return full_dir_path


if __name__ == "__main__":
    print('Starting now -- please wait until finished')

    # 1) Scrape data, build your maps
    setUpAnnualAndQuarterlyObjects()       # presumably does the scraping
    annual_ticker_map = setUpAnnualTickerMap()
    quarterly_ticker_map = setUpQuarterlyTickerMap()

    print('===============================================')
    for key, value in quarterly_ticker_map.items():
        print(key, value) 
    print('-----------------------------------------------')
    print('===============================================')
    for key, value in annual_ticker_map.items():
        print(key, value) 
    print('-----------------------------------------------')

    # 2) Create the "Annual-<timestamp>" directory
    annual_base_dir = setUpDirectories('Annual', tickers)
    for ticker in tickers:
        createAnnualStockTxtFile(ticker, annual_base_dir)

    # 3) Create the "Quarterly-<timestamp>" directory
    quarterly_base_dir = setUpDirectories('Quarterly', tickers)
    for ticker in tickers:
        createQuarterlyStockTxtFile(ticker, quarterly_base_dir)

    # 4) Create your Excel workbooks
    createAnnualExcelWorkbook()
    createQuarterlyExcelWorkbook()
    createFutureExcelWorkbook()
    print('Finished!')
