from datetime import datetime
from time import sleep
import json
import asyncio


from parser import makeProductsQueue, parseProductPage


async def main():
    date = str(datetime.now()).split(".")[0]
    data = []

    queue = makeProductsQueue()
    for link in queue:
        result = await parseProductPage(link)
        data.append(result)

    with open (f"results/{date}.json", "w+", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{date}.json записан")


if __name__ == "__main__":
    asyncio.run(main())
