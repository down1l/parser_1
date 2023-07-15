import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup as soup


from time import sleep
import re
import json
from typing import Union


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
            # [1:] - удаление "/" в начале строки-ссылки
            main_links[link] = URL + main_links[link]["href"][1:]
        return main_links
    return 0


def getLinksForPages(url: str) -> Union[list, int]:
    """
    Данная функция берет ссылки на страницы из категорий
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        parser = soup(html, "html.parser")
        links = parser.find_all("li", class_="page")
        return links[1:]  # первый элемент списка - открытая страница
    return 0


def getProductslinks(url):
    """
    Данная функция берет ссылки на страницы из категорий
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        parser = soup(html, "html.parser")
        links = parser.find_all("div", class_="goodsHeader")
        return links
    return 0


def main():
    products_queue = []
    pages_queue = []
    count = 0

    main_links = getLinksFromMainPage()
    if main_links:
        for link in main_links:
            pages_queue.append(link)
            pages_links = getLinksForPages(link)
            if pages_links:
                for page_link in pages_links:
                    # Регулярное выражение для поиска страниц категорий
                    pattern = r"/shop/\w+/page/\d"
                    result = re.search(pattern, str(page_link))
                    # Добавление в очередь для последубщего парсинга страниц
                    pages_queue.append(f"{URL}{result.group(0)[1:]}")
    for pop in pages_queue:
        products_links = getProductslinks(pop)
        # print(pop)
        if products_links:
            for product in products_links:
                count += 1
                pattern = r'<a\s+href="([^"]+)"'
                result = re.search(pattern, str(product)).group(1)
                products_queue.append(f"{URL}{result[1:]}")
                # print(f"----{URL}{result[1:]}")
                # print(f"----{product}")

    for product in products_queue:
        print(product)
    print(len(products_queue))


if __name__ == "__main__":
    main()
