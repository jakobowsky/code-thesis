from clients.SeleniumClient import SeleniumClient
from clients.FileClient import FileClient, FileType

def selenium_scraping(asin: str, client: SeleniumClient, file_client: FileClient):
    data = client.get_item(asin, solve_captcha=False)
    file_client.write(data, FileType.RAW_DATA, f'{asin}.json')
    return data