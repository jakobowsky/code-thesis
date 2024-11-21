import requests
import urllib.parse

from decouple import config
from utils.decorators.calculate_time import calculate_time

class SpApiClient:
    def __init__(self, marketplace="ATVPDKIKX0DER"):
        self.marketplace = marketplace
        self.refresh_token = config('SP_API_LWA_REFRESH_TOKEN')
        self.client_id = config('SP_API_LWA_ID')
        self.client_secret = config('SP_API_LWA_SECRET')
        self.access_token = self.get_access_token()

    def get_access_token(self):
        url = f"https://api.amazon.com/auth/o2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        token_response = requests.post(url, data=data)
        access_token = token_response.json().get('access_token')
        return access_token
        
    @calculate_time
    def get_item(self, asin: str):
        url = f"https://sellingpartnerapi-na.amazon.com/catalog/2022-04-01/items/{asin}"
        params = {
            "marketplaceIds": self.marketplace,
            "includedData": "attributes,classifications,dimensions,identifiers,images,productTypes,salesRanks,summaries,relationships"
        }
        headers = {
            "x-amz-access-token": self.access_token
        }

        request_url = f"{url}?{urllib.parse.urlencode(params)}"
        response = requests.get(request_url, headers=headers)

        return response.json() if response.status_code == 200 else {}

    def get_title(self, data: dict):
        try:
            response = data["summaries"][0]["itemName"]
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_brand(self, data: dict):
        try:
            response = data["summaries"][0]["brand"]
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_manufacturer(self, data: dict):
        try:
            response = data["summaries"][0]["manufacturer"]
        except Exception as e:
            response = ""
            print(e)
        return response
    
    def get_description(self, data: dict):
        try:
            description = data["attributes"]["bullet_point"]
            description = "\n".join(list(map(lambda x: x["value"].strip(), description)))
        except Exception as e:
            description = ""
            print(e)
        return description
    
    def get_images(self, data: dict):
        try:
            images = data["images"][0]["images"]
            images = list(map(lambda x: x["link"], images))
        except Exception as e:
            images = []
            print(e)
        return images
    
    def get_price(self, data: dict):
        try:
            response = data["attributes"]["list_price"][0]["value"]
        except Exception as e:
            response = 0
            print(e)
        return response

    def parse_item(self, data: dict, asin: str):
        return {
            "asin": asin,
            "title": self.get_title(data),
            "brand": self.get_brand(data),
            "manufacturer": self.get_manufacturer(data),
            "description": self.get_description(data),
            "images": self.get_images(data),
            "price": self.get_price(data),
            "time": data["time"]
        }