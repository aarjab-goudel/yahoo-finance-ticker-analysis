#!/usr/bin/env python3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests
import constants

global_driver = None

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



def getStatisticsRowByText(soup, text, tag_name):
    text_tag_results = soup.find_all(lambda tag: tag.name == tag_name and text in tag.text)
    if text_tag_results:
        for text_tag in text_tag_results:
            if text_tag.text == text:
                row_tag = text_tag.parent.parent
                return row_tag
    else:
        print('Error in getting  ' + text + ' from this tag: ' + tag_name)
        return None

def getProfileValueFromRowByText(soup, text, tag_name):
    profile_row = getStatisticsRowByText(soup, text, tag_name)
    mini_soup = BeautifulSoup(str(profile_row), "html.parser")
    profile_td = mini_soup.find_all('td')[1]
    return profile_td.text

def getRowValueFromStatisticsRow(soup, text, tag_name):
    row_tag = getStatisticsRowByText(soup, text, tag_name)
    if row_tag:
        stat_map = {text: ''}
        mini_soup = BeautifulSoup(str(row_tag), "html.parser")
        td_tags = mini_soup.find_all('td')
        for td_tag in td_tags:
            if text not in td_tag.text:
                stat_map[text] = td_tag.text
        return stat_map
    else:
        return None


def getRowByText(soup, text, tag_name):
    text_tag_results = soup.find_all(lambda tag: tag.name == tag_name and text in tag.text)
    if text_tag_results:  
        for text_tag in text_tag_results:
            if text_tag.text == text:
                row_tag = text_tag.parent.parent.parent
                return row_tag
    else:
        print('Error in getting ' + text + ' from this tag: ' + tag_name)
        return None

def getRowValuesByText(soup, text, tag_name):
    row_tag = getRowByText(soup, text, tag_name)
    if row_tag:
        row_map = {text: []}
        mini_soup = BeautifulSoup(str(row_tag), "html.parser")
        span_tags = mini_soup.find_all('span')
        for span_tag in span_tags:
            if span_tag.text != text:
                row_map[text].append(span_tag.text)
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

def getDriver():
    global global_driver
    if not global_driver:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        global_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return global_driver
    else:
        return global_driver

def quitDriver():
    global global_driver
    global_driver.close()
    global_driver.quit()
    global_driver = None



def clickQuarterlyButton(url):
    try:
        driver = getDriver()
        driver.get(url)
        WebDriverWait(driver, constants.SLEEP_TIME).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button'))).click()
        time.sleep(constants.SLEEP_TIME)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        return soup 
    except Exception as e:
        print('-------------------------------------------------')
        print('EXCEPTION OCCURED IN CLICK QUARTERLY BUTTON !!!!')
        print(e)
        print('-------------------------------------------------')
        return None


def clickOperatingExpense(url):
    try:
        driver = getDriver()
        driver.get(url)
        WebDriverWait(driver, constants.SLEEP_TIME).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']"))).click()
        WebDriverWait(driver, constants.SLEEP_TIME).until(EC.element_to_be_clickable((By.XPATH, "//div[@title='Operating Expense']/button[@aria-label='Operating Expense']"))).click()
        time.sleep(constants.SLEEP_TIME)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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


def readDataFromPageSource(soup, label, tag):
    try:
        row = getRowValuesByText(soup, label, tag)[label]
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



        


    

