from clients.RainforestClient import RainforestClient
from clients.FileClient import FileClient, FileType

def rainforest_scraping(asin: str, client: RainforestClient, file_client: FileClient):
    data = client.get_item(asin)
    file_client.write(data, FileType.RAW_DATA, f'{asin}.json')
    return client.parse_item(data) if data else {}