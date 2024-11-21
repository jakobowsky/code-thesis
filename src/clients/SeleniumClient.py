import re
import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from amazoncaptcha import AmazonCaptcha
from utils.const import MARKETPLACE_BASE_URL, USER_AGENTS
from utils.decorators.calculate_time import calculate_time

class SeleniumClient:
    def __init__(self):
        self.base_url = MARKETPLACE_BASE_URL
        chrome_options = Options()
        chrome_options.add_argument(f"--user-agent={USER_AGENTS[0]}")
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--browser_version=eager")
        self.driver = webdriver.Chrome(options=chrome_options)

    def change_user_agent(self, user_agent):
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})

    def set_driver_latency(self, latency=2, download_throughput=400 * 1024, upload_throughput=400 * 1024):
        self.driver.set_network_conditions(offline=False, latency=latency, download_throughput=download_throughput, upload_throughput=upload_throughput)

    def solve_captcha(self):
        solution = None
        try:
            img_src = self.driver.find_element(by= By.CSS_SELECTOR, value="form .a-box-inner img").get_attribute('src')
            if not img_src:
                return None
            captcha = AmazonCaptcha.fromlink(img_src)
            solution = captcha.solve(keep_logs=True)
            print(solution)
            input = self.driver.find_element(by= By.ID, value="captchacharacters")
            input.send_keys(solution)

            submit = self.driver.find_element(by= By.CSS_SELECTOR, value="form button[type='submit']")
            submit.click()
        except Exception as e:
            print(e)
        return solution

    def load_site(self, asin, solve_captcha):
        try:
            url = urllib.parse.urljoin(self.base_url, f'/dp/{asin}')
            self.driver.get(url)
            if solve_captcha:
                solution = self.solve_captcha()
                return 1 if solution else 0
        except Exception as e:
            print(e)
            chrome_options = Options()
            chrome_options.add_argument(f"--user-agent={USER_AGENTS[0]}")
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--browser_version=eager")
            self.driver = webdriver.Chrome(options=chrome_options)
        return 0

    def get_title(self):
        try:
            title = self.driver.find_element(by= By.ID, value="productTitle").text
        except Exception as e:
            title = ""
            print(e)
        return title

    def get_stars(self):
        try:
            stars = self.driver.find_element(by= By.CSS_SELECTOR, value="#acrPopover a > span.a-size-base").text
            stars = stars.strip().replace(",", ".")
            stars = float(stars)
        except Exception as e:
            stars = 0
            print(e)
        return stars
    
    def get_ratings_quantity(self):
        try:
            ratings_quantity = re.search("^\d+\,\d+", self.driver.find_element(by= By.ID, value="acrCustomerReviewText").text).group(0)
            ratings_quantity = int(ratings_quantity.strip().replace(",", ""))
        except Exception as e:
            ratings_quantity = 0
            print(e)
        return ratings_quantity
    
    def get_price(self):
        try:
            whole = self.driver.find_element(by= By.CSS_SELECTOR, value="#corePriceDisplay_desktop_feature_div > .a-section .a-price-whole").text
            whole = re.search('^\d+', whole.strip().replace("€", "")).group(0)
            decimal = self.driver.find_element(by= By.CSS_SELECTOR, value="#corePriceDisplay_desktop_feature_div > .a-section .a-price-fraction").text
            price = f"{whole}.{decimal}"
            price = float(price)
        except Exception as e:
            price = 0
            print(e)
        return price
    
    def get_description(self):
        try:
            description = self.driver.find_element(by= By.ID, value="feature-bullets").text
        except Exception as e:
            description = ""
            print(e)
        return description
    
    def get_images(self):
        try:
            images = self.driver.find_elements(by= By.CSS_SELECTOR, value="#altImages .a-button-thumbnail img")
            images = [image.get_attribute('src') for image in images]
        except Exception as e:
            images = []
            print(e)
        return images
    
    def get_brand(self):
        try:
            table = self.driver.find_element(by= By.ID, value="productOverview_feature_div")
            table_rows = table.find_elements(by= By.CSS_SELECTOR, value="tr")
            brand=""
            for row in table_rows:
                cells = row.find_elements(by= By.CSS_SELECTOR, value="span")
                if cells[0].text.lower() == "brand":
                    brand = cells[1].text
        except Exception as e:
            brand = ""
            print(e)
        return brand
    
    def get_manufacturer(self):
        try:
            manufacturer = ""
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-csa-c-func-deps=aui-da-voyager-expand-all-handler]"))
            )
            expandButton = self.driver.find_element(by=By.CSS_SELECTOR, value="[data-csa-c-func-deps=aui-da-voyager-expand-all-handler]")
            if not expandButton:
                return manufacturer
            expandButton.click()
            accordions = self.driver.find_elements(by=By.CSS_SELECTOR, value="[data-csa-c-content-id=voyager-expander-btn-t2] table tr")
            for accordion in accordions:
                cells = accordion.find_elements(by=By.CSS_SELECTOR, value="th,td")
                cells = list(cells)

                for i in range(len(cells) - 1):
                    if cells[i].text.lower() == "manufacturer":
                        manufacturer = cells[i+1].text
                        break
        except Exception as e:
            manufacturer = ""
            print(e)
        return manufacturer



    def get_product_data(self):
        try:
            title = self.get_title()
            stars = self.get_stars()
            ratings_quantity = self.get_ratings_quantity()
            price = self.get_price()
            description = self.get_description()
            images = self.get_images()
            brand = self.get_brand()
            manufacturer = self.get_manufacturer()

            return {
                'title': title,
                'brand': brand,
                'manufacturer': manufacturer,
                'description': description,
                'images': images,
                'price': price,
                'stars': stars,
                'ratings_quantity': ratings_quantity,
            }
        except Exception as e:
            return {}
    
    @calculate_time
    def get_item(self, asin, solve_captcha=True):
        captcha = self.load_site(asin, solve_captcha)
        time.sleep(0.5)
        data = {"asin": asin, "captcha": captcha, **self.get_product_data()}
        return data
        
    