import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup as soup

from time import sleep
import re


URL = "https://www.zveromir.ru/"


def getLinksFromMainPage(url=URL) -> list:
    """
    Данная функция берет ссылки из главной страницы
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        parser = soup(html, "html.parser")
        main_links = parser.find_all("a", class_="do-popdown")
        for link in range(len(main_links)):
            main_links[link] = URL + main_links[link]["href"][1:]
        return main_links
    return 0


def getLinksForCategory(url: str) -> list:
    """
    Данная функция берет ссылки на страницы из категорий
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        parser = soup(html, "html.parser")
        main_links = parser.find_all("li", class_="page")
        return main_links[1:]  # первый элемент списка - открытая страница
    return 0


def main():
    main_links = getLinksFromMainPage()
    if main_links:
        for link in main_links:
            pages_links = getLinksForCategory(link)
            print(f"{link}")
            if pages_links:
                for page_link in pages_links:
                    pattern = r"/shop/\w+/page/\d"
                    result = re.search(pattern, str(page_link))

                    print(f"---- {URL}{result.group(0)[1:]}")
            print()


if __name__ == "__main__":
    main()
