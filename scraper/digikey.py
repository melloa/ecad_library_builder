import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time


DIGIKEY = "https://www.digikey.com"
PRODUCTS = "/products/en?keywords="


# TODO real logging
def log(key: object, val: object) -> object:
    print(str(key) + ": " + str(val))


def search(driver, partnumber):
    pdf_url, man, details = part_info(partnumber)
    sym = symbol(pdf_url)
    foot = footprint(pdf_url)
    return {"pdf_url":pdf_url, "manufacturer":man, "symbol":sym, "footprint":foot}


def symbol(pdf_url):
    # TODO implement
    return "sym"


def footprint(pdf):
    # TODO implement
    return "foot"


def part_info(driver, part_number):
    search_url = DIGIKEY + PRODUCTS + part_number
    log(search_url, search_url)
    driver.get(search_url)
    # TODO create wait
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
    return pdf_url, man, DIGIKEY + details_page


if __name__ == "__main__":
    driver = webdriver.Firefox()
    print(part_info(driver, "KSZ8993M"))
    driver.quit()