# import aiohttp
# import asyncio
import requests
from bs4 import BeautifulSoup as soup


from typing import Union

from .config import URL


def getLinksFromMainPage(url=URL) -> Union[list, int]:
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
