from httpx import AsyncClient
from lxml import etree
from lxml.etree import HTMLParser


import os
import gc
import asyncio
from typing import Union
import re
import json
from datetime import datetime
import time


URL = "https://www.zveromir.ru/"


class ParseException(Exception):
    pass


async def GetLinksFromMainPage(url: str) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки на категории из главной страницы
    """
    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        category_links = tree.xpath('//a[@class="do-popdown"]/@href')
        # [1:] - удаление "/" в начале строки-ссылки
        return [url + link[1:] for link in category_links]

    raise ParseException(f"Неудачный запрос на главную страницу {url}")


async def GetLinksOfPagesCategory(url: str) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки на страницы категорий
    """

    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        pages_links = tree.xpath('//li[@class="page"]/a/@href')

        if len(pages_links) != 0:
            # [1:] - удаление "/" в начале строки-ссылки
            return [url] + [URL + link[1:] for link in pages_links]
        else:
            return [url]

    raise ParseException(
        f"Неудачный запрос на первую страницу категории {url}")


async def MakeCategoryPagesQueue(category_main_links: list) -> list:
    """
    Функция для создания списка всех ссылок на страницы категорий с обработкой ошибок запроса
    """
    category_pages_queue = []

    for link in category_main_links:
        try:
            pages_links = await GetLinksOfPagesCategory(link)

            for page_link in pages_links:
                category_pages_queue.append(page_link)

        except ParseException as e:
            print(f"Ошибка: {e}")

    return category_pages_queue


async def GetProductslinks(url: str) -> Union[list, ParseException]:
    """
    Данная функция берет ссылки на страницы товаров на основе списка всех страниц с товарами
    """
    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        products_links = tree.xpath('//div[@class="goodsHeader"]/a/@href')
        products_links = [URL + link[1:] for link in products_links]
        return products_links

    else:
        raise ParseException(
            f"Неудачный запрос на страницу категории {url}")


async def MakeProductsQueue(pages_queue: list) -> list:
    """
    Функция для создания списка всех ссылок на товары с обработкой ошибок запроса
    """
    products_queue = []

    for url in pages_queue:
        try:
            pages_links = await GetProductslinks(url)

            for product_link in pages_links:
                products_queue.append(product_link)

        except ParseException as e:
            print(f"Ошибка: {e}")

    return products_queue


async def ParseProductPrise(url: str) -> Union[str, ParseException]:

    dump_keys = ["Имя", "ID", "Вес", "Цена", "Бренд",
                 "Ссылка на картику",  "Описание", "Наличие", "Вложенность категорий"]

    dump_data = []

    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())

        # Имя
        name = tree.xpath(
            '//h1[@class="h1 h1--card-page d-none d-lg-block"]/text()')[0]

        dump_data.append(name)
        # ID
        id_ = int(url.split("/")[-2].split("-")[0])
        dump_data.append(id_)
        # Вес
        weight = tree.xpath(
            '//div[@class="card-product-type-item__val"]/text()')

        if len(weight) == 0:
            weight = '-'
        elif len(weight) == 1:
            weight = weight[0]
        else:
            weight == ', '.join(weight)

        dump_data.append(weight)
        # Цена
        price = tree.xpath('//span[@itemprop="price"]/@content')

        if len(price) == 1:
            price = price[0]

            # Наличие
            if int(price) != 0:
                available = "True"
            else:
                available = "False"

        else:
            # Наличие
            available = "True"
            price == ', '.join(price)

        dump_data.append(price)
        # Бренд
        brand = tree.xpath('//div[@class="breadcrumbListInner"]/a/text()')[-1]

        dump_data.append(brand)
        # Ссылка на картику
        img_url = URL + \
            tree.xpath('//img[@class="eslider-main-img hitem"]/@src')[0][1:]

        dump_data.append(img_url)
        # Описание
        description = tree.xpath(
            '//div[@class="tab-pane fade show active"]//text()')
        for row_index in range(len(description)):
            description[row_index] = re.sub(
                r"\s+", " ",  description[row_index].strip().replace("\n", " "))
        description = re.sub(r"\n+", "\n", "\n".join(description)).strip("\n")

        dump_data.append(description)
        dump_data.append(available)
        # Вложенность категорий
        category = "/".join(tree.xpath(
            '//div[@class="breadcrumbListInner"]/a/text()'))

        dump_data.append(category)
        return dict(zip(dump_keys, dump_data))

    else:
        raise ParseException(
            f"Неудачный запрос на страницу товара {url}")


async def MakeProductsDump(products_links: list) -> None:
    dump = []

    for url in products_links:
        try:
            product_dump = await ParseProductPrise(url)
            dump.append(product_dump)

        except ParseException as e:
            print(f"Ошибка: {e}")

    date = str(datetime.now()).split(" ")[0]
    with open(f"results/{date}.json", "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)

    print(f"Данные записаны в results/{date}.json")


async def main() -> None:
    try:
        category_main_links = await GetLinksFromMainPage(URL)

    except ParseException as e:
        print(f"Ошибка: {e}")

    if category_main_links:
        category_pages_links = await MakeCategoryPagesQueue(category_main_links)

    if category_pages_links:  # Если список не пустой
        products_links = await MakeProductsQueue(category_pages_links)

    if products_links:  # Если список не пустой
        await MakeProductsDump(products_links)

    # Очистка оперативной памяти
    del (category_main_links, category_pages_links, products_links)
    gc.collect()


if __name__ == "__main__":
    while True:
        asyncio.run(main())

        time.sleep(5 * 24 * 60 * 60)
