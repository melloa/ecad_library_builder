import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import argparse, sys



DIGIKEY = "https://www.digikey.com"
SEARCH = "/products/en?keywords="
CATEGORIES = "/products/en/integrated-circuits-ics/32?pkeyword=&keywords=&v=&newproducts=1"
CATEGORIES_DATASHEETS = CATEGORIES + "&datasheet=1"


# TODO real logging
def log(key, val):
    print(str(key) + ": " + str(val))


def search(driver, part_number):
    search_url = DIGIKEY + SEARCH + part_number
    log(search_url, search_url)
    driver.get(search_url)
    # TODO proper wait
    time.sleep(5)
    elem = driver.find_element_by_xpath('//*[@id="productTable"]/tbody')
    html = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(html, features='html.parser')
    if soup is None:
        log("couldn't parse", "")
        return None
    tr = soup.find("tr")
    if tr is None:
        log("couldn't parse", "")
        return None
    #TODO make concurrent
    details_page = tr.find("td", class_="tr-mfgPartNumber").find("a")["href"]
    pdf_url = tr.find("td", class_="tr-datasheet").find("a")["href"]
    #TODO make cleaning common
    man = tr.find("td", class_="tr-vendor").get_text().strip().strip("\n").lower().replace(" ", "-")
    return [pdf_url, man, details_page]

# scrapes all parts
def scape_all():
    pass

# scrapes parts for category
def scrape_category(driver, cat):
    parts = categoy_parts(driver, cat)
    part_info = [cat]
    for p in parts():
        part_info.append(p)
        part_info += search(p)
    print(part_info)


# gets all categories for integrated circuits
def categories(driver):
    return []

# gets all parts for category
def categoy_parts(driver, cat):
    return []


if __name__ == "__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument('--search_part', help='Provide a part number to search', type=str)
    parser.add_argument('--get_category', help='Provide a part number to search', type=str)
    parser.add_argument('--scrap_category', help='Provide a part number to search', type=str)
    args = parser.parse_args()
    print(args.search_part)

    driver = webdriver.Firefox()
    if 'search_part' in args:
        log("searching", args.search_part)
        print(search(driver, args.search_part))
    driver.quit()
