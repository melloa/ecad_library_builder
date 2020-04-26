import requests
from google.cloud import datastore
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import argparse, sys
from store.store import set_part


PART_TYPE = 'part'
DIGIKEY = "https://www.digikey.com"
SEARCH = "/products/en?keywords="
CATEGORIES = "/products/en/integrated-circuits-ics/32?pkeyword=&keywords=&v=&newproducts=1"
CATEGORIES_DATASHEETS = CATEGORIES + "&datasheet=1"
HEADERS = "part_number, pdf, manufacturer, details_page"


# TODO real logging
def log(key, val):
    print(str(key) + ": " + str(val))


def clean(s):
    return s.strip().strip("\n").lower()


def get_parts_info(tr):
    if tr is None:
        log("couldn't parse", "")
        return None
    #TODO make concurrent
    details_page = DIGIKEY + tr.find("td", class_="tr-mfgPartNumber").find("a")["href"]
    if details_page is None:
        log("couldn't parse details", "")
        return None
    pdf_url = tr.find("td", class_="tr-datasheet").find("a")["href"]
    if pdf_url is None:
        log("couldn't parse pdf", "")
        return None
    man = clean(tr.find("td", class_="tr-vendor").get_text()).replace(" ", "-").replace(",","")
    if man is None:
        log("couldn't parse vendor", "")
        return None
    part_number = clean(tr.find("td", class_="tr-mfgPartNumber").find("span").get_text())
    if part_number is None:
        log("couldn't parse part number", "")
        return None
    return {"number":part_number, "pdf":pdf_url, "manufacturer":man, "details_page":details_page}


def search(driver, part_number):
    search_url = DIGIKEY + SEARCH + part_number
    log(search_url, search_url)
    driver.get(search_url)
    # TODO proper wait
    time.sleep(5)
    table = driver.find_element_by_xpath('//*[@id="productTable"]/tbody')
    html = table.get_attribute('innerHTML')
    soup = BeautifulSoup(html, features='html.parser')
    if soup is None:
        log("couldn't parse", "")
        return None
    tr = soup.find("tr")
    return get_parts_info(tr)


# scrapes all parts
def scrape_all(driver, dc):
    cats = scrape_categories(driver)
    log("found cats", "")
    with open("out.csv", "w") as out:
        # out.write(HEADERS + '\n')
        for cat in cats:
            # name = cat[0]
            link = cat[1]
            parts = scrape_category(driver, link)
            if parts is None:
                log("skipping", link)
                continue
            for part in parts:
                if dc == None:
                    for data in part:
                        out.write(data + ",")
                    out.write("\n")
                else:
                    set_part(dc, part)
                log("stored part", part)
            time.sleep(5) # don't get blocked


# scrapes parts for category
def scrape_category(driver, cat_url):
    cat_url += "&pageSize=1000"
    driver.get(cat_url)
    # TODO proper wait
    time.sleep(5)
    try:
        table = driver.find_element_by_xpath('//*[@id="lnkPart"]')
    except:
        log("could not scrape cat", cat_url)
        return None
    html = table.get_attribute('innerHTML')
    soup = BeautifulSoup(html, features='html.parser')
    if soup is None:
        log("couldn't parse", "")
        return None
    trs = soup.find_all("tr")
    parts_info = []
    for tr in trs:
        part_info = get_parts_info(tr)
        if part_info is None:
            continue
        parts_info.append(part_info)
    return parts_info


# gets all categories for integrated circuits
def scrape_categories(driver):
    driver.get(DIGIKEY + CATEGORIES_DATASHEETS)
    time.sleep(5)
    ul = driver.find_element_by_xpath('//*[@id="productIndexList"]/ul')
    html = ul.get_attribute('innerHTML')
    soup = BeautifulSoup(html, features='html.parser')
    if soup is None:
        log("couldn't parse", "")
        return None
    lis = soup.find_all("li")
    cats = []
    for li in lis:
        a = li.find("a")
        link = DIGIKEY + a["href"]
        # log("link", link)
        name = clean(a.get_text()).replace(" ", "")
        # log("name", name)
        cats.append([name, link])
    return cats


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--scrape_part', help='Scrape info based on a part number', type=str)
    parser.add_argument('--scrape_categories', help='Scrape all IC categories', type=bool)
    parser.add_argument('--scrape_category', help='Scrape all part info for a category', type=str)
    parser.add_argument('--scrape_all', help='Scrape all parts info', type=bool)
    parser.add_argument('--dump', help='Dump data to cloud', type=bool)
    args = parser.parse_args()
    print(args)
    driver = webdriver.Firefox()
    if not(args.scrape_part is None):
        log("searching", args.scrape_part)
        print(search(driver, args.scrape_part))
    elif not(args.scrape_categories is None):
        log("scrape categories", args.scrape_categories)
        print(scrape_categories(driver))
    elif not(args.scrape_category is None):
        log("scrape category", args.scrape_category)
        print(scrape_category(driver, args.scrape_category))
    elif not(args.scrape_all is None):
        log("scrape all", args.scrape_all)
        dc = None
        if not(args.dump is None):
            dc = datastore.Client(project='thiq-275323')
        scrape_all(driver, dc)
    else:
        print("invalid options")
    driver.quit()
