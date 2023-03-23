import pandas as pd
from datetime import datetime
from common_service import *
import requests
class StockObj:
    def __init__(self, ticker):
        self.ticker = ticker
        self.industry = ''
        self.sector = ''
        self.peRatio = ''
        self.dividend = ''
        self.fullName = ''
        self.currency = ''
        
    def getYahooFinancialDataProfileUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/profile?p=' + ticker

    def getYahooFinancialDataQuoteUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '?p=' + ticker

    def getYahooFinancialDataUrl(self, ticker):
        return 'https://finance.yahoo.com/quote/' + ticker + '/financials?p=' + ticker

    


def printStockObj(stockObj):
    print('Industry')
    print(stockObj.industry)
    print('Sector')
    print(stockObj.sector)
    print('PE Ratio')
    print(stockObj.peRatio)
    print('Dividend')
    print(stockObj.dividend)
    print('Full Name')
    print(stockObj.fullName)
    print('Currency')
    print(stockObj.currency)

def readCommonStockData(ticker):
    stockObj = StockObj(ticker)
    try:
        response = requests.get(stockObj.getYahooFinancialDataProfileUrl(ticker), headers=getHeader())
        print('Common Stock Response Code for ' + ticker + ' is ' + str(response.status_code))
        soup = BeautifulSoup(response.content, "html.parser")
        main_section_div = soup.find_all("div", {"class": "asset-profile-container"})
        div_soup = BeautifulSoup(str(main_section_div), "html.parser")
        stockObj.fullName = div_soup.find_all('h3')[0].text
        profile_row = getProfileTexyByTicker(soup, 'Sector(s)', 'span')
        mini_soup = BeautifulSoup(str(profile_row), "html.parser")
        span_tags = mini_soup.find_all('span')
        stockObj.sector = span_tags[1].text
        stockObj.industry = span_tags[3].text

        stock_summary_response = requests.get(stockObj.getYahooFinancialDataQuoteUrl(ticker), headers=getHeader())
        stock_summary_soup = BeautifulSoup(stock_summary_response.content, "html.parser")
        stockObj.peRatio = getProfileValueFromRowByText(stock_summary_soup, 'PE Ratio (TTM)', 'span')
        stockObj.dividend = getProfileValueFromRowByText(stock_summary_soup, 'Forward Dividend & Yield', 'span')

        financial_response = requests.get(stockObj.getYahooFinancialDataUrl(ticker), headers=getHeader())
        second_soup = BeautifulSoup(financial_response.content, "html.parser")
        stockObj.currency = readCurrencyType(second_soup, 'All numbers in thousands', 'span')

        

        printStockObj(stockObj)
        return stockObj
    except Exception as e:
        print(e)
        stockObj.industry = 'ERROR'
        stockObj.sector = 'ERROR'
        stockObj.peRatio = 'ERROR'
        stockObj.dividend = 'ERROR'
        stockObj.fullName = 'ERROR'
        stockObj.currency = 'ERROR'
        return stockObj
