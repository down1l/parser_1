from time import sleep
import re
import json


from parser import getLinksForPages,\
    getLinksFromMainPage,\
    getProductslinks,\
    URL,\
    PAGES_RE,\
    PRODUCTS_RE


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
                    result = re.search(PAGES_RE, str(page_link))
                    # Добавление в очередь для последубщего парсинга страниц
                    pages_queue.append(f"{URL}{result.group(0)[1:]}")
    for pop in pages_queue:
        products_links = getProductslinks(pop)
        # print(pop)
        if products_links:
            for product in products_links:
                count += 1
                result = re.search(PRODUCTS_RE, str(product)).group(1)
                products_queue.append(f"{URL}{result[1:]}")
                # print(f"----{URL}{result[1:]}")
                # print(f"----{product}")

    for product in products_queue:
        print(product)
    print(len(products_queue))


if __name__ == "__main__":
    main()
