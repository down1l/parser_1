import requests
from httpx import AsyncClient, Response  # Response - для аннотации
from bs4 import BeautifulSoup as soup


import os
from textwrap import TextWrapper as tw
from typing import Union
import re
import json


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


async def parseProductPage(url: str) -> str:
    async with AsyncClient() as client:
        response = await client.get(url)
    result = parseProductPrise(response)
    return result


def parseProductPrise(response: Response) -> Union[str, int]:

    description_txt = ""
    product_json = {}
    parser = soup(response.text, "html.parser")

    price = parser.find("span", itemprop="price").text
    name = parser.find("h1", class_="h1 h1--card-page d-none d-lg-block").text
    id = str(response.url).split("\\")[-1]
    try:
        size = parser.find("div", class_="card-product-type-item__val").text
    except AttributeError:
        pass
    
    img_url = parser.find("img", class_="eslider-main-img hitem").get("src")

    description = parser.find(
        "div", class_="tab-pane fade show active").children
    for par in description:
        if "Нужна консультация? Звоните!" not in par.text:
            description_txt += par.text
        else:
            break
    description_txt = " ".join(tw(width=60).wrap(text=description_txt))

    product_json["id"] = int(re.search(r"\d+", id).group(0))
    product_json["имя"] = name
    product_json["цена"] = int(re.search(r"\d+", price).group(0))

    if size:
        product_json["размер"] = size

    if product_json["цена"] == 0:
        product_json["наличие"] = "нет в наличии"
    else:
        product_json["наличие"] = "в наличии"

    product_json["картинка"] = URL + img_url[1:]
    product_json["ссылка"] = str(response.url)
    product_json["описание"] = re.sub(r"\s+", " ", description_txt)

    return product_json
