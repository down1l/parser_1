import requests
from bs4 import BeautifulSoup as soup


from typing import Union
import re

from .config import URL, PAGES_RE, PRODUCTS_RE


def getLinksFromMainPage(url=URL) -> Union[list, int]:
    """
    Данная функция берет ссылки из главной страницы
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        parser = soup(html, "html.parser")
        main_links = parser.find_all("a", class_="do-popdown")
        # [1:] - удаление "/" в начале строки-ссылки
        return [URL + link["href"][1:] for link in main_links]
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


def getProductslinks(url: str) -> Union[list, int]:
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


def makePagesQueue(links: list) -> list:
    """
    Данная функция делает список всех ссылок на страницы с товарами
    """
    queue = []
    for link in links:
        queue.append(link)
        pages_links = getLinksForPages(link)
        if pages_links:
            for page_link in pages_links:
                result = re.search(PAGES_RE, str(page_link))
                # Добавление в очередь для последующего парсинга страниц
                queue.append(f"{URL}{result.group(0)[1:]}")
    return queue


def makeProductsQueue():
    """
    Данная функция делает список ссылок на страницы всех товаров
    """
    products_queue = []

    links = getLinksFromMainPage()
    if links:
        pages_queue = makePagesQueue(links)
    for link in pages_queue:
        products_links = getProductslinks(link)
        if products_links:
            for product in products_links:
                result = re.search(PRODUCTS_RE, str(product)).group(1)
                products_queue.append(f"{URL}{result[1:]}")
    return products_queue
