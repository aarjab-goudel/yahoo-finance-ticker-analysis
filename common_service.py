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
from datetime import datetime
import time
import requests
import constants
import re

_playwright = None
_browser = None
_page = None

def open_browser():
    """
    Opens the Playwright browser exactly once and returns a reference to the page.
    If already open, returns the existing page.
    """
    global _playwright, _browser, _page
    if not _playwright:
        _playwright = sync_playwright().start()
    if not _browser:
        # Launch browser in headless mode
        _browser = _playwright.chromium.launch(headless=True)
    if not _page:
        _page = _browser.new_page()
    return _page

def close_browser():
    """
    Closes the Playwright browser if it's open.
    """
    global _playwright, _browser, _page
    if _page:
        _page.close()
        _page = None
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None



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

def getStatisticsDatesByText(soup, text_label):
    """
    Find the <th> that has the given text (e.g., 'Current'),
    then extract all the <th> values from the parent <tr>.
    """
    # 1. Find the <th> that contains the text_label
    label_th = soup.find("th", text=re.compile(text_label))
    if not label_th:
        print(f'Error: Could not find header with text "{text_label}"')
        return None
    
    # 2. Get the parent <tr> of that <th>
    row = label_th.find_parent("tr")
    if not row:
        print(f'Error: Could not find row for header "{text_label}"')
        return None
    
    # 3. Grab all <th> in that row
    ths = row.find_all("th")
    
    # 4. Return the text from each <th>, stripped of extra whitespace
    return [th.get_text(strip=True) for th in ths]


def getStatisticsTableByText(soup, text_label):

    # 1. Find the <td> that contains the text label
    label_td = soup.find("td", text=re.compile(text_label))
    if not label_td:
        print(f'Error: Could not find label "{text_label}"')
        return None

    # 2. Get the parent <tr> of that <td>
    row = label_td.find_parent("tr")
    if not row:
        print(f'Error: Could not find row for label "{text_label}"')
        return None

    # 3. Grab all <td> in that row (you can refine the class_ if needed)
    tds = row.find_all("td")

    # 4. Extract text from each <td> and strip whitespace
    #    The first td is the label; the subsequent ones are the values.
    return [td.get_text(strip=True) for td in tds]

def getPEGRatios(soup):

    label_td = soup.find("td", string="PEG Ratio (5yr expected)")
    if not label_td:
        print(f'Error: Could not find label "{label_td}"')
        return None

    row = label_td.find_parent("tr")
    if not row:
        print(f'Error: Could not find row for label "{label_td}"')
        return None

    tds = row.find_all("td")
    return [td.get_text(strip=True) for td in tds]


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

def getRowValuesByText(soup, text, is_quarterly):
    row_tag = getRowByText(soup, text)
    if not row_tag:
        return None

    # Split the row text into an array of values
    val_arr = row_tag.strip().split()

    # Decide how many items we want to grab
    target_len = 5 if is_quarterly else 4

    # Slice the last N items
    row_arr = val_arr[-target_len:]

    # If row_arr is too short, prepend 'ERROR' until it's length N
    while len(row_arr) < target_len:
        row_arr.insert(0, 'ERROR')

    # print(row_arr)

    # Build and return the dictionary
    row_map = {text: row_arr}
    return row_map



def is_valid_number(num):
    """
    Returns True if s is a number that can contain commas and a negative sign, False otherwise.
    """
    if num == 'ERROR' or num == '--':
        return True
    try:
        float(num.replace(',', ''))
        return True
    except ValueError:
        return False

def is_data_quarterly(soup):
    """
    Returns True if the 'Breakdown' row has consecutive dates
    whose differences are <= 100 days (approx. 3 months).
    Otherwise, returns False.
    """
    # Grab the array of date strings for the 'Breakdown' row
    dates = readDataFromPageSource(soup, 'Breakdown', True)  # e.g. ["9/30/2024", "6/30/2024", ...]

    # Attempt to parse each date string into a datetime object
    parsed_dates = []
    for ds in dates:
        try:
            # Format is "m/d/yyyy" e.g. "9/30/2024"
            parsed_dt = datetime.strptime(ds.strip(), "%m/%d/%Y")
            parsed_dates.append(parsed_dt)
        except Exception:
            # If parsing fails, might be a placeholder like '0.000'
            pass

    # If we couldn't parse at least 2 valid dates, we can't confirm quarterly intervals
    if len(parsed_dates) < 2:
        return False

    # Sort them so we can check consecutive differences
    parsed_dates.sort()

    # Check consecutive day differences
    for i in range(len(parsed_dates) - 1):
        diff_days = (parsed_dates[i+1] - parsed_dates[i]).days
        # If difference is more than ~100 days, it's likely annual or not updated
        if diff_days > 120:
            return False

    # If all consecutive pairs are <= 100 days, it looks like quarterly data
    return True

def clickQuarterlyButton(page, url):
    """
    Attempts up to MAX_ATTEMPTS times to:
      1) goto(url) [domcontentloaded],
      2) wait a bit, click the 'Quarterly' button,
      3) wait a bit, parse the DOM,
      4) verify we have quarterly data (is_data_quarterly(soup)).

    If successful, returns the soup. Otherwise raises Exception.
    """
    MAX_ATTEMPTS = 5

    for attempt in range(MAX_ATTEMPTS):
        print(f"[Attempt {attempt+1}/{MAX_ATTEMPTS}] Loading {url}")

        try:
            # 1) Go to the page, only wait until DOM is parsed (less strict than networkidle)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2) Sleep a bit to allow JS to run after DOMContentLoaded
            time.sleep(5)

            # 3) Wait for the 'Quarterly' button to appear, click it
            page.wait_for_selector("text=Quarterly", timeout=60000)
            page.click("text=Quarterly")

            # 4) Sleep again so the table can update to quarterly
            time.sleep(10)

            # 5) Parse the HTML
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # 6) Check if it's quarterly
            if is_data_quarterly(soup):
                print(">> Verified: data is Quarterly!")
                return soup
            else:
                print(f">> Not Quarterly yet, retrying... attempt {attempt+1}")
                time.sleep(5)  # short sleep before next attempt

        except Exception as e:
            print("-------------------------------------------------")
            print(f"Exception in clickQuarterlyButton (attempt {attempt+1}):")
            print(e)
            print("-------------------------------------------------")
            # short sleep, then retry from the top
            time.sleep(5)

    # If we exhausted all attempts
    return None




def clickOperatingExpense(page, url):
    MAX_ATTEMPTS = 5
    for attempt in range(MAX_ATTEMPTS):
        print(f"[Attempt {attempt+1}/{MAX_ATTEMPTS}] Loading {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            time.sleep(5)

            # Wait for the button to appear
            page.wait_for_selector("button[aria-label='Operating Expense']", timeout=60000)

            # Click the Operating Expense button
            page.click("button[aria-label='Operating Expense']")

            # Give some time for the page to update after clicking
            time.sleep(5)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")
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
        for i in range(len(dates)):
            if dates[i] == '--':
                dates[i] = 'ERROR'

        for j in range(len(dates)):
            if dates[j] == '--':
                dates[j] = 'ERROR'

        while len(dates) != len(row_values) and len(dates) > len(row_values):
            row_values.insert(0, '0.000')
    return row_values

def handleEmptyDateList(dates):
    if not dates:
        return ['0.000', '0.000', '0.000', '0.000']
    else:
        return dates


def readDataFromPageSource(soup, label, is_quarterly):
    try:
        row = getRowValuesByText(soup, label, is_quarterly)[label]
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

def parse_numeric_value(value):
    # Remove commas and convert to float

    if (',' in value):
        return float(value.replace(',', ''))
    if '0.000' in value:
        return 0
    if 'ERROR' in value:
        return 'ERROR'
    if not value or '':
        return 'ERROR'
    value_no_letters = re.sub(r'[a-zA-Z]', '', value)
    try:
        return float(value_no_letters)
    except Exception as e:
        return 'ERROR'

def calculateEBITDAInterst(ebitda, interest):
    numeric_ebitda = parse_numeric_value(ebitda)
    numeric_interest = parse_numeric_value(interest)

    if numeric_interest == 0:
        return 'ERROR'
    
    ebitda_interest_rate = numeric_ebitda / numeric_interest
    return f"{ebitda_interest_rate:.2f}"



def percent_change(beginning_str, end_str):
    # Convert input strings to floats
    beginning = parse_numeric_value(beginning_str)
    end = parse_numeric_value(end_str)

    if beginning == 'ERROR' or end == 'ERROR':
        return 'ERROR'

    # Handle the case where beginning is 0 (to avoid division by zero)
    if beginning == 0:
        if end == 0:
            # No change if both are zero
            return "+0.0%"
        else:
            # Arbitrary decision: if beginning=0 and end != 0, treat as +/-∞
            return "+∞%" if end > 0 else "-∞%"

    # Calculate percent change
    ratio = (end - beginning) / abs(beginning)  # e.g. 0.056 -> 5.6%
    ratio_percent = ratio * 100

    # Build the output string, including sign
    sign_str = "+" if ratio_percent >= 0 else ""  # negative already includes '-'
    return f"{sign_str}{ratio_percent:.2f}%"

def removeDecimalFromStr(value_str):
    """
    Removes any decimal portion from the given string.
    If there's a period in the string, everything from
    the period onward is removed.

    Examples:
        "351,002,000.00" -> "351,002,000"
        "351,002,000.35" -> "351,002,000"
        "351,002,000"    -> "351,002,000"
    """
    if '.' in value_str:
        # Split at the first '.' and take everything before it
        value_str = value_str.split('.', 1)[0]
    return value_str

def stripAlphabetFromNum(val):
    allowed_chars = set("0123456789-.,")
    return ''.join(ch for ch in val if ch in allowed_chars)






        


    

