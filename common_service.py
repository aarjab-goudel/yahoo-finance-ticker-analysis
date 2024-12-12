#!/usr/bin/env python3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from playwright.sync_api import sync_playwright
import time
import requests
import constants

def getHeader():
    # Set up the request headers that we're going to use, to simulate
    # a request by the Chrome browser. Simulating a request from a browser
    # is generally good practice when building a scraper
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'close',
        'DNT': '1', # Do Not Track Request Header 
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    return headers

def getProfileTexyByTicker(soup, text, tag_name):
    text_tag_results = soup.find_all(lambda tag: tag.name == tag_name and text in tag.text)
    if text_tag_results:
        for text_tag in text_tag_results:
            if text_tag.text == text:
                row_tag = text_tag.parent
                return row_tag
    else:
        print('Error in getting  ' + text + ' from this tag: ' + tag_name)
        return None



def getStatisticsRowByText(soup, text):
    # HERE IS WHERE WE ARE SCRAPING THE DATA FROM THE WEB PAGE
    tds = soup.find_all("td", class_=lambda c: c and ("label" in c or "value" in c))
    if tds:
        for index, td in enumerate(tds):
            if text in str(td):
                value = tds[index+1]
                return value
    else:
        print('Error in getting  ' + text)
        return None

def getProfileValueFromRowByText(soup, text):
    profile_row = getStatisticsRowByText(soup, text)
    mini_soup = BeautifulSoup(str(profile_row), "html.parser")
    profile_td = mini_soup.find_all('td')[1]
    return profile_td.text

def getRowValueFromStatisticsRow(soup, text):
    row_tag = getStatisticsRowByText(soup, text)
    if row_tag:
        stat_map = {text: row_tag.get_text(strip=True)}
        return stat_map
    else:
        return None


def getRowByText(soup, text):
    # HERE IS WHERE WE ARE SCRAPING THE DATA FROM THE WEB PAGE
    divs = soup.find_all("div", class_="row")
    if divs:  
        for item in divs:
            div = item.get_text(strip=False)
            if text in div:
                return div
    else:
        print('Error in getting ' + text)
        return None
    return None

def getRowValuesByText(soup, text):
    row_tag = getRowByText(soup, text)
    if row_tag:
        val_arr = row_tag.strip().split()
        row_arr = val_arr[-4:]
        row_map = {text: row_arr}
        return row_map
    else:
        return None


def is_valid_number(num):
    """
    Returns True if s is a number that can contain commas and a negative sign, False otherwise.
    """
    try:
        float(num.replace(',', ''))
        return True
    except ValueError:
        return False

def is_xpath_valid(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except Exception as e:
        return False


def clickQuarterlyButton(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # Click the Quarterly button
            page.wait_for_selector("text=Quarterly")
            page.click("text=Quarterly")

            # Wait for the page to update
            time.sleep(5)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            browser.close()
            return soup
    except Exception as e:
        print('-------------------------------------------------')
        print('EXCEPTION OCCURED IN CLICK QUARTERLY BUTTON !!!!')
        print(e)
        print('-------------------------------------------------')
        return None



def clickOperatingExpense(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # Wait for the button to appear
            page.wait_for_selector("button[aria-label='Operating Expense']")

            # Click the Operating Expense button
            page.click("button[aria-label='Operating Expense']")

            # Give some time for the page to update after clicking
            time.sleep(5)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            browser.close()
            return soup
    except Exception as e:
        print('-------------------------------------------------')
        print('EXCEPTION OCCURED IN CLICK OPERATING EXPENSE!!!!')
        print(e)
        print('-------------------------------------------------')
        return None

def cleanRowValues(dates, row_values):
    if not dates:
        return ['0.000', '0.000', '0.000', '0.000']
    else:
        while len(dates) != len(row_values) and len(dates) > len(row_values):
            row_values.insert(0, '0.000')
    return row_values

def handleEmptyDateList(dates):
    if not dates:
        return ['0.000', '0.000', '0.000', '0.000']
    else:
        return dates


def readDataFromPageSource(soup, label):
    try:
        row = getRowValuesByText(soup, label)[label]
        return row
    except:
        error_row = ['0.000', '0.000', '0.000', '0.000']
        return error_row

def readHeaderCurrencyType(soup):
    try:
        currency_div = soup.find_all('div')[0]
        span_text = currency_div.find_all('span')[constants.CURRENCY_INDEX].text.split('.')
        currency_text = span_text[1].strip()
        currency = currency_text.split(' ')[2]
        return currency
    except Exception as e:
        print('-------------------------------------------------')
        print('EXCEPTION OCCURED IN READ HEADER CURRENCY TYPE!!!!')
        print(e)
        print('-------------------------------------------------')
        return 'ERROR'

def readCurrencyType(soup, text, tag_name):
    try:
        currency_tag_results = soup.find_all(lambda tag: tag.name == tag_name and text in tag.text)
        span_tag = currency_tag_results[1]
        span_text = span_tag.text
        if (span_text == text):
            return readHeaderCurrencyType(soup)
        else:
            split_text = span_text.split(".")[0]
            currency_type = split_text.split(" ")[2]
            return currency_type
    except Exception as e:
        print('-------------------------------------------------')
        print('EXCEPTION OCCURED IN READ CURRENCY TYPE!!!!')
        print(e)
        print('-------------------------------------------------')
        return 'ERROR'



        


    

