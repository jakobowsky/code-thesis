import requests
import urllib.parse

from decouple import config
from utils.decorators.calculate_time import calculate_time

class RainforestClient:
    def __init__(self):
        self.api_key = config('RAINFOREST_API_KEY')
        self.base_url = "https://api.rainforestapi.com/request"

    @calculate_time
    def get_item(self, asin: str):
        params = {
            "api_key": self.api_key,
            "amazon_domain": "amazon.com",
            "asin": asin,
            "type": "product",
            "currency": "usd",
            "output": "json"
        }

        response = requests.get(
            f"{self.base_url}?{urllib.parse.urlencode(params)}"
        )

        return response.json() if response.status_code == 200 else {}

    def get_title(self, data: dict):
        try:
            response = data["product"]["title"]
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_brand(self, data: dict):
        try:
            response = data["product"]["brand"]
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_manufacturer(self, data: dict):
        try:
            response = data["product"]["manufacturer"]
        except Exception as e:
            response = ""
            print(e)
        return response

    def get_description(self, data: dict):
        try:
            response = data["product"]["feature_bullets"]
            response = "\n".join(response)
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_images(self, data: dict):
        try:
            response = data["product"]["images"]
            response = list(map(lambda x: x["link"], response))
        except Exception as e:
            response = []
            print(e)
        return response
    
    def get_price(self, data: dict):
        try:
            response = data["product"]["buybox_winner"]["price"]["value"]
        except Exception as e:
            response = 0
            print(e)
        return response
    
    def get_rating(self, data: dict):
        try:
            response = data["product"]["rating"]
        except Exception as e:
            response = 0
            print(e)
        return response
    
    def get_ratings_total(self, data: dict):
        try:
            response = data["product"]["ratings_total"]
        except Exception as e:
            response = 0
            print(e)
        return response

    def parse_item(self, data: dict):
        return {
            "title": self.get_title(data),
            "brand": self.get_brand(data),
            "manufacturer": self.get_manufacturer(data),
            "description": self.get_description(data),
            "images": self.get_images(data),
            "price": self.get_price(data),
            "rating": self.get_rating(data),
            "ratings_total": self.get_ratings_total(data),
            "time": data["time"]
        }