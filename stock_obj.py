#!/usr/bin/env python3
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

    def __repr__(self):
        return f"StockObj(ticker={self.ticker}, industry={self.industry}, sector={self.sector}, peRatio={self.peRatio}, dividend={self.dividend}, fullName={self.fullName}, currency={self.currency})"

    


def printStockObj(stockObj):
    print('Industry')
    print('--------')
    print(stockObj.industry)
    print('Sector')
    print('--------')
    print(stockObj.sector)
    print('PE Ratio')
    print('--------')
    print(stockObj.peRatio)
    print('Dividend')
    print('--------')
    print(stockObj.dividend)
    print('Full Name')
    print('--------')
    print(stockObj.fullName)
    print('Currency')
    print('--------')
    print(stockObj.currency)

def readCommonStockData(ticker):
    stockObj = StockObj(ticker)
    try:
        response = requests.get(stockObj.getYahooFinancialDataProfileUrl(ticker), headers=getHeader())
        print('Common Stock Response Code for ' + ticker + ' is ' + str(response.status_code))
        soup = BeautifulSoup(response.content, "html.parser")
        if soup:
            sections = soup.find("section", {"data-testid": "asset-profile"})
            if sections:
                # Extract the h3 heading
                heading_tag = sections.find("h3", class_="header")
                stockObj.fullName = heading_tag.get_text(strip=True)
                link_tags = sections.find_all("a", class_="subtle-link")
                index = 0
                for link_tag in link_tags:
                    if index == 0:
                        stockObj.sector = link_tag.get_text(strip=True)
                    if index == 1:
                        stockObj.industry = link_tag.get_text(strip=True)
                    index = index + 1

        stock_summary_response = requests.get(stockObj.getYahooFinancialDataQuoteUrl(ticker), headers=getHeader())
        stock_summary_soup = BeautifulSoup(stock_summary_response.content, "html.parser")

        if stock_summary_soup:
            div = stock_summary_soup.find("div", {"data-testid": "quote-statistics"})
            if div:
                ul = div.find("ul")
                if ul:
                    list_items = ul.find_all("li")
                    for li in list_items:
                        label_span = li.find("span", class_="label")
                        value_span = li.find("span", class_="value")

                        if label_span and value_span:
                            label_text = label_span.get_text(strip=True)
                            value_text = value_span.get_text(strip=True)

                            if "PE Ratio (TTM)" in label_text:
                                stockObj.peRatio = value_text
                            elif "Forward Dividend & Yield" in label_text:
                                stockObj.dividend = value_text

        financial_response = requests.get(stockObj.getYahooFinancialDataUrl(ticker), headers=getHeader())
        currency_soup = BeautifulSoup(financial_response.content, "html.parser")
        if currency_soup:
            span = currency_soup.find("span", class_="currency")
            stockObj.currency = span.get_text(strip=True)       
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

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Balance Sheet analysis for a given ticker.")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    args = parser.parse_args()
    
    # Use the ticker passed from the command line to read the annual BS data
    bsObj = readCommonStockData(args.ticker)