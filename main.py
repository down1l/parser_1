import requests
from bs4 import BeautifulSoup as soup

from time import sleep


URL = "https://www.zveromir.ru/"

def getLinksFromMainPage(url = URL) -> list:
    html = requests.get(URL).text
    parser = soup(html, "html.parser")
    main_links = parser.find_all("a", class_ ="do-popdown")
    for link in range(len(main_links)):
        main_links[link] = main_links[link]["href"]
    return main_links

main_links = getLinksFromMainPage()
print(main_links)