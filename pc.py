import re
import csv
import os
import io
import time

import requests
from bs4 import BeautifulSoup
from pushover import Client
from dotenv import load_dotenv
import boto3
import botocore


if os.getenv("ENV") == "development":
    load_dotenv()

PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
PUSHOVER_USER_TOKEN = os.getenv("PUSHOVER_USER_TOKEN")
ITEMS_URL = os.getenv("ITEMS_URL")
BUCKET_NAME = ps.getenv("BUCKET_NAME")
KEY = ps.getenv("KEY")



def get_addresses():
    addresses = []
    
    s3 = boto3.resource('s3')
    s3.Bucket(BUCKET_NAME).download_file(KEY, 'items.csv')

    csv_file = open('items.csv')
    reader = csv.DictReader(csv_file)

    for row in reader:
        address = row['url']
        addresses.append(address)

    csv_file.close()

    return (addresses)


def send_message(title, message):
    push = Client(PUSHOVER_USER_TOKEN, api_token=PUSHOVER_API_TOKEN)  # create the pushover object
    push.send_message(message, title=title)


def main(addresses):
    for url in addresses:
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')

        current_price = soup.find('span', class_=re.compile(r'currentPrice'))  # returns a list
        orig_price = soup.find('span', class_=re.compile(r'originalPrice'))  # returns a list
        title = soup.find("title").contents[0]
        title = title.partition(" |")[0]  # remove | Nordstrom from the title
        current_price = float(current_price.contents[0][1:])

        if orig_price is not None:
            orig_price = float(orig_price.contents[0][1:])

            if current_price < orig_price:

                title = "Nordstrom's price drop alert!"
                message = (f"The price of {title} has dropped! Original price:  ${orig_price} \
                            New price: ${current_price}. Here's the link: {url}\n")

                send_message(title, message)
                print("Found some stuff on sale, sending you a message!")

        print(f"{title} is not on sale, sorry!")

        time.sleep(1)

if __name__ == "__main__":
    main(get_addresses())  # get addresses returns addresses which gets passed to main
