import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import winsound
from datetime import datetime as time
import json
import re

timeout = 8  # seconds of timeout for the webdriver to wait for an element to be present


def beep():
    frequency = 440
    duration = 1000
    winsound.Beep(frequency, duration)


class WGGesuchtCrawler:
    def __init__(self, driver_options=None, args=None):
        self.driver = None
        self.offers = None
        self.setup_chrome_driver(driver_options, args)

    def setup_chrome_driver(self, driver_options=None, args=None):
        args = args or []
        driver_options = driver_options or {}

        chrome_options = Options()

        for (k, v) in driver_options.items():
            chrome_options.add_experimental_option(k, v)
        for arg in args:
            chrome_options.add_argument(arg)

        # create the initial window
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self, email, password):

        # go to the home page
        self.driver.get('https://www.wg-gesucht.de')

        while True:
            try:
                self.driver.find_element_by_xpath('//*[@id="cmpwelcomebtncustom"]').click()
                break
            except:
                pass

        # Cookies
        self.driver.find_element_by_xpath('//a[contains(., "Save")]').click()

        # Sign in
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[a[contains(., "Mein Konto")]]')))
        self.driver.find_element_by_xpath('//div[a[contains(., "Mein Konto")]]').click()

        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id ="login_email_username"]')))
        self.driver.find_element_by_xpath('//*[@id ="login_email_username"]').send_keys(email)
        self.driver.find_element_by_xpath('//*[@id ="login_password"]').send_keys(password)
        self.driver.find_element_by_xpath('//div[input[@id ="login_submit"]]').click()

        while True:
            try:
                self.driver.find_element_by_xpath('//div[a[@id ="hide_login_show_register"]]')
            except:
                break
            sleep(0.2)

        return self.driver

    def custom_filter_search(self):
        self.driver.find_element_by_xpath('//input[@id ="autocompinp"]').send_keys("München")
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='autocomplete-suggestions']/div[contains(., 'ünchen')]")))
        self.driver.find_element_by_xpath(
            "//div[@class ='autocomplete-suggestions']/div[contains(., 'ünchen')]").click()
        self.driver.find_element_by_xpath('//input[@id ="search_button"]').click()
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//ul[@id ="user_filter"]/li/a')))
        self.driver.find_element_by_xpath('//ul[@id ="user_filter"]/li/a').click()

    def enlist_offers(self):
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "offer_list_item")))
        self.offers = self.driver.find_elements(By.CLASS_NAME, "offer_list_item")

    def get_offer_online_time(self, offer: WebElement) -> int:
        time_online_str = offer.find_element_by_xpath("//span[contains(text(), \"Online\")]").text
        try:
            minutes = int(re.match(r'Online: (\d+) Minuten', time_online_str).group(1))
        except:
            minutes = 10000
        return minutes

    def handle_offer(self, offer: WebElement):
        if self.get_offer_online_time(offer) < 20:
            beep()
            print("New offer at {}".format(time.now().strftime("%H:%M:%S")))

    def handle_offers(self):
        for offer in self.offers:
            self.handle_offer(offer)

    def refresh(self):
        self.driver.refresh()
        print("Page refreshed at {}".format(time.now().strftime("%H:%M:%S")))
        self.enlist_offers()

    def run(self):
        while True:
            self.refresh()
            self.handle_offers()
            sleep(random.randint(60, 180))


def main():
    config_path = "config.json"
    config = json.load(open(config_path))

    email = config["email"]
    password = config["password"]

    driver_options = {"useAutomationExtension": False,
                      "excludeSwitches": ["enable-automation"],
                      "prefs": {"credentials_enable_service": False,
                                "profile.password_manager_enabled": False}
                      }
    args = ["--start-fullscreen", "--headless", "window-size=1920x1080"]

    crawler = WGGesuchtCrawler(driver_options=driver_options, args=args)
    crawler.login(email, password)
    crawler.custom_filter_search()

    crawler.run()


if __name__ == "__main__":
    main()
