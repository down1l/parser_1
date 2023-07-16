from time import sleep
import re
import json


from parser import makeProductsQueue


def main():
    queue = makeProductsQueue()
    print(len(queue))


if __name__ == "__main__":
    main()
