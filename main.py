import requests
from time import sleep

while True:
    sleep(3)
    status_code = requests.get("https://www.zveromir.ru/shop").status_code
    print(status_code)
    