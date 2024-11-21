from clients.SpApiClient import SpApiClient
from clients.FileClient import FileClient, FileType

def spapi_scraping(asin: str, spApiClient: SpApiClient, file_client: FileClient):
    data = spApiClient.get_item(asin)
    file_client.write(data, FileType.RAW_DATA, f'{asin}.json')
    return spApiClient.parse_item(data, asin) if data else {"asin": asin}