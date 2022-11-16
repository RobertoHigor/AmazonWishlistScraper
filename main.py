import argparse
import scraper
import telebot
import sqlite3
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WISHLIST_URL = os.environ.get('WISHLIST_URL')
DESTINATION = os.environ.get('DESTINATION')

bot = telebot.TeleBot(BOT_TOKEN)

def is_on_sale(item):
        last_item = check_if_exists(item)
        if last_item is None:
                add_item(item)
                add_item_history(item)
                return False
       
        add_item_history(item)
        update_item(item)
        currentPrice = item['price']
        lastPrice = item['price']
        if currentPrice < lastPrice:
                return True
     
def add_item(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'INSERT INTO wishlist (id, title, price) VALUES ("{item["id"]}", "{item["title"]}", {item["price"]})'
        cursor.execute(aux)
        conn.commit()
        conn.close()

def add_item_history(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'INSERT INTO wishlist_history (ProductId, Price, DatePrice) VALUES ("{item["id"]}", {item["price"]}, datetime("now"))'
        cursor.execute(aux)
        conn.commit()
        conn.close()
def update_item(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'UPDATE wishlist SET price = {item["price"]} WHERE Id ="{item["id"]}"'
        cursor.execute(aux)
        conn.commit()
        conn.close()

def check_if_exists(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'SELECT Id, Title, Price FROM wishlist WHERE Id = "{item["id"]}"'
        cursor.execute(aux)
        data = cursor.fetchone()
        conn.close()
        return data

wishlist_data = scraper.get_data(WISHLIST_URL)

for item in wishlist_data:
        sale = is_on_sale(item)
        if sale:
                itemMessage = f"# {item['title']} \n Está em promoção custando: {item['price']}"
                bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')

print("Finished")