import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime as time
import json
import re

from playsound import playsound

timeout = 40  # seconds of timeout for the webdriver to wait for an element to be present


def beep(times=1):
    for i in range(times):
        playsound('audio/notification_sound.mp3')


class WGGesuchtCrawler:
    def __init__(self, email, password, driver_options=None, args=None):
        self.email = email
        self.password = password
        self.driver = None
        self.new_offers = None
        self.seen_offers = []
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

    def login(self):

        # go to the home page
        self.driver.get('https://www.wg-gesucht.de')

        print("Waiting for cookies...")
        while True:
            try:
                self.driver.find_element(By.XPATH, '//a[contains(., "Settings")]').click()
                break
            except:
                pass

        # Cookies
        self.driver.find_element(By.XPATH, '//a[contains(., "Save")]').click()

        # Sign in
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[a[contains(., "Mein Konto")]]')))
        self.driver.find_element(By.XPATH, '//div[a[contains(., "Mein Konto")]]').click()

        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id ="login_email_username"]')))
        self.driver.find_element(By.XPATH, '//*[@id ="login_email_username"]').send_keys(self.email)
        self.driver.find_element(By.XPATH, '//*[@id ="login_password"]').send_keys(self.password)
        self.driver.find_element(By.XPATH, '//div[input[@id ="login_submit"]]').click()

        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, '//div[a[@id ="hide_login_show_register"]]')))

        print("Logged in")

    def custom_filter_search(self):
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@id ="autocompinp"]')))

        self.driver.find_element(By.XPATH, '//input[@id ="autocompinp"]').send_keys("München")
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='autocomplete-suggestions']/div[contains(., 'ünchen')]")))
        self.driver.find_element(By.XPATH,
                                 "//div[@class ='autocomplete-suggestions']/div[contains(., 'ünchen')]").click()
        self.driver.find_element(By.XPATH, '//input[@id ="search_button"]').click()
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//ul[@id ="user_filter"]/li/a')))
        self.driver.find_element(By.XPATH, '//ul[@id ="user_filter"]/li/a').click()

    def get_new_offers(self):
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "offer_list_item")))
        unfiltered_new_offers = self.driver.find_elements(By.XPATH,
                                                          '//div[contains(@class, "offer_list_item") and not(contains(@class, "cursor-pointer"))]')
        self.new_offers = []
        for offer in unfiltered_new_offers:
            online_time = self.get_offer_online_time(offer)
            if online_time < 60:
                self.new_offers.append(offer)

    @staticmethod
    def get_offer_online_time(offer: WebElement) -> int:
        offer_text = offer.text
        try:
            minutes = int(re.match(r'Online: (\d+) Minuten', offer_text).group(1))
        except:
            minutes = 61
        return minutes

    def handle_offer(self, offer: WebElement):
        if hash(offer.text[:30]) not in self.seen_offers:
            beep()
            print("-" * 50 + "\n")
            print("New offer at {}".format(time.now().strftime("%H:%M:%S")))
            print(offer.text)
            self.seen_offers.append(hash(offer.text[:30]))

    def handle_offers(self):
        for offer in self.new_offers:
            self.handle_offer(offer)

    def refresh(self):
        self.driver.refresh()
        self.get_new_offers()

    def run(self):
        self.login()
        self.custom_filter_search()
        print("Starting to crawl...")

        # Initial listing of offers
        self.get_new_offers()
        for offer in self.new_offers:
            self.seen_offers.append(hash(offer.text[:30]))

        # Main loop checking for new offers
        while True:
            sleep(random.randint(60, 180))
            self.refresh()
            self.handle_offers()


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
    args = ["--start-fullscreen", "--headless", "window-size=1920x1080", "--log-level=3"]
    crawler = WGGesuchtCrawler(email, password, driver_options=driver_options, args=args)
    crawler.run()


if __name__ == "__main__":
    main()
