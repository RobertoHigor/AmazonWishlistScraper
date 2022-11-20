import scraper
import telebot
import sqlite3
import os
import logging

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

        precoAtual = item['price']
        precoAnterior = last_item['price']
        # Somente salvar se houve mudança de preco
        if precoAtual != precoAnterior:
                add_item_history(item)
                update_item(item) 

        # Não salvar se preço for 0
        if precoAtual <= 0:
                return False
        elif precoAtual > 0 and precoAnterior == 0:
                aviso_volta_estoque(item)
                return False     

        if item['oferta'] is not None or precoAtual < precoAnterior:
                return True        

        return False


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

def aviso_volta_estoque(item):
        itemMessage = f"# {item['title']} \n Está de volta em estoque custando: {item['price']}"
        bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')

def remover_precos_duplicados_historico():
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'DELETE FROM wishlist_history WHERE Id not in (select Id from wishlist_history group by ProductId, Price)'
        cursor.execute(aux)
        conn.commit()
        conn.close()

wishlist_data = scraper.get_data(WISHLIST_URL)

for item in wishlist_data:
        # Executar script se for switch oled
        if item['id'] == 'I3KMIYEAPY0NB5':
                logging.info(f"Removendo preços duplicados por conter {item['title']} na lista")
                remover_precos_duplicados_historico()

        sale = is_on_sale(item)
        if sale and item['oferta'] is not None:
                logging.info(f"Enviando item {item['title']} em promoção por {item['price']}")
                itemMessage = f"# {item['title']} \n Está em oferta Amazon custando: {item['price']}"
                bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')
        elif sale:
                logging.info(f"Enviando item {item['title']} voltando em estoque por {item['price']}")
                itemMessage = f"# {item['title']} \n Está em promoção custando: {item['price']}"
                bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')

print("Finalizando")