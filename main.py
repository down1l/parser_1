from time import sleep
import json
import asyncio


from parser import makeProductsQueue, parseProductPage


async def main():
    queue = makeProductsQueue()

    for link in queue:
        result = await parseProductPage(link)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
