import os
import re
import time
import random
import requests
import urllib.parse

from lxml import html

from utils.const import USER_AGENTS

class CrawlClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, asin):
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        url = urllib.parse.urljoin(self.base_url, f'/dp/{asin}')
        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)

        return response, tree
    
    def get_title(self, tree):
        try:
            title = tree.xpath('//span[@id="productTitle"]/text()')[0]
        except Exception as e:
            title = ""
            print(e)
        return title
    
    def get_brand(self, tree):
        try:
            brand = tree.xpath('//*[@id="productOverview_feature_div"]/div/table/tbody/tr[1]/td[2]/span/text()')[0]
        except Exception as e:
            brand = ""
            print(e)
        return brand
    
    def get_manufacturer(self, tree):
        try:
            manufacturer = tree.xpath('//div[@id="detailBullets_feature_div"]/ul/li[span/span[1][contains(text(), "Manufacturer")]]/span/span[2]/text()')[0]
        except Exception as e:
            manufacturer = ""
            print(e)
        return manufacturer
    
    def get_description(self, tree):
        try:
            description = tree.xpath('//div[@id="feature-bullets"]')[0]
            description = str(description)
        except Exception as e:
            description = ""
            print(e)
        return description
    
    def get_images(self, tree):
        try:
            images = tree.xpath('//div[@id="altImages"]/ul/li//img/@src')
        except Exception as e:
            images = []
            print(e)
        return images
    
    def get_price(self, tree):
        try:
            price=tree.xpath('//div[@id="a-popover-agShipMsgPopover"]/table/tr[1]/td[3]/span/text()')[0]
            price = float(re.sub(r"[^\d.]", "", price))
            price = float(price)
        except Exception as e:
            price = 0
            print(e)
        return price
    
    def get_stars(self, tree):
        try:
            stars = tree.xpath('//span[@id="acrPopover"]//span[contains(@class, "a-size-base")]/text()')[0]
            print(stars)
            stars = float(re.sub(r"[^\d.]", "", stars))
            print(stars)
        except Exception as e:
            stars = 0
            print(e)
        return stars
    
    def get_ratings_quantity(self, tree):
        try:
            ratings_quantity = tree.xpath('//span[@id="acrCustomerReviewText"]/text()')[0]
            ratings_quantity = int(re.sub(r"[^\d.]", "", ratings_quantity))
        except Exception as e:
            ratings_quantity = 0
            print(e)
        return ratings_quantity
    
    def get_product_data(self, tree):
        try:
            title = self.get_title(tree)
            stars = self.get_stars(tree)
            ratings_quantity = self.get_ratings_quantity(tree)
            price = self.get_price(tree)
            description = self.get_description(tree)
            images = self.get_images(tree)
            brand = self.get_brand(tree)
            manufacturer = self.get_manufacturer(tree)

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
    
    def save(self, asin: str, filepath: str):
        response = self.get(asin)

        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w') as file:
            file.write(response.text)
        return filepath
    
    def get_item(self, asin):
        start = time.time()

        try:
            for _ in range(10):
                response, tree = self.get(asin)
                product_data = self.get_product_data(tree)

                product_data = {
                    'asin': asin,
                    **product_data
                }

                if product_data['title']:
                    break
                else:
                    time.sleep(0.5)
        except Exception as e:
            response = {"text": ""}
            product_data = {
                'asin': asin,
                'title': '',
                'brand': '',
                'manufacturer': '',
                'description': '',
                'images': [],
                'price': 0,
                'stars': 0,
                'ratings_quantity': 0,
            }
            print(e)

        end = time.time()
        product_data['time'] = end - start

        return response, product_data