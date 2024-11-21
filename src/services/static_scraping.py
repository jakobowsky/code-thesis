from clients.CrawlClient import CrawlClient
from clients.FileClient import FileClient, FileType

def static_scraping(client: CrawlClient, file_client: FileClient, asin: str):
    try:
        html, data = client.get_item(asin)
        if html and html.status_code == 200:
            file_client.write(html.text, FileType.RAW_DATA, f"{asin}.html")
    except Exception as e:
        print(e)
        data = {'asin': asin}
    return data