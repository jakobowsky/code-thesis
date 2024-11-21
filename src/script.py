import datetime
import argparse

from services.static_scraping import static_scraping
from services.selenium_scraping import selenium_scraping
from services.spapi_scraping import spapi_scraping
from services.rainforest_scraping import rainforest_scraping
from utils.asins import dataset
from clients.FileClient import FileClient, FileType
from clients.SpApiClient import SpApiClient
from clients.RainforestClient import RainforestClient
from clients.SeleniumClient import SeleniumClient
from clients.CrawlClient import CrawlClient

from enum import Enum
from collections import defaultdict

class ScrapingType(Enum):
    SP_API = "spapi"
    RAINFOREST = "rainforest"
    SELENIUM = "selenium"
    STATIC = "static"

    def __str__(self):
        return self.value

result_filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def main(crawl_type: str=ScrapingType.SP_API):
    if(crawl_type == ScrapingType.SP_API):
        '''
        SP-API Client
        '''
        spApiFileClient = FileClient('./results/sp_api', './raw_data/sp_api')
        spApiClient = SpApiClient()
        sp_api_data = defaultdict(list)
        for category, asins in dataset.items():
            for asin in asins:
                response = spapi_scraping(asin, spApiClient, spApiFileClient)
                sp_api_data[category].append(response)
        spApiFileClient.write(sp_api_data, FileType.RESULTS, f'{result_filename}.json')
    elif(crawl_type == ScrapingType.RAINFOREST):
        '''
        Rainforest Client
        '''
        rainforestFileClient = FileClient('./results/rainforest', './raw_data/rainforest')
        rainforestClient = RainforestClient()
        rainforest_data = defaultdict(list)
        for category, asins in dataset.items():
            for asin in asins:
                response = rainforest_scraping(asin, rainforestClient, rainforestFileClient)
                rainforest_data[category].append(response)
        rainforestFileClient.write(rainforest_data, FileType.RESULTS, f'{result_filename}.json')
    elif(crawl_type == ScrapingType.SELENIUM):
        '''
        Selenium Client
        '''
        seleniumFileClient = FileClient('./results/selenium', './raw_data/selenium')
        seleniumClient = SeleniumClient()
        selenium_data = defaultdict(list)

        rotate_agent = False
        for category, asins in dataset.items():
            for index, asin in enumerate(asins):
                if(rotate_agent):
                    seleniumClient.change_user_agent(seleniumClient.user_agents[index % len(seleniumClient.user_agents)])
                response = selenium_scraping(asin, seleniumClient, seleniumFileClient)
                selenium_data[category].append(response)
        seleniumFileClient.write(selenium_data, FileType.RESULTS, f'{result_filename}.json')
    elif(crawl_type == ScrapingType.STATIC):
        '''
        Static Data
        '''
        staticFileClient = FileClient('./results/static', './raw_data/static')
        crawlClient = CrawlClient('https://www.amazon.com')
        static_data = defaultdict(list)
        for category, asins in dataset.items():
            for asin in asins:
                response = static_scraping(crawlClient, staticFileClient, asin)
                static_data[category].append(response)
        staticFileClient.write(static_data, FileType.RESULTS, f'{result_filename}.json')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=ScrapingType, choices=list(ScrapingType), help='Scraping Method for experiments: spapi, rainforest, selenium, static')
    args = parser.parse_args()
    main(args.type)
