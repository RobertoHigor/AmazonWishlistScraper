import scraper
import telebot
import sqlite3
import os
import logging

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WISHLIST_URL = os.environ.get('WISHLIST_URL')
DESTINATION = os.environ.get('DESTINATION')
DISCOUNT = os.environ.get('DISCOUNT').replace(',', '.')

bot = telebot.TeleBot(BOT_TOKEN)

def is_on_sale(item):
        last_item = check_if_exists(item)
        if last_item is None:
                add_item(item)
                add_item_history(item)
                return False, 0

        precoAtual = item['price']
        precoAnterior = last_item['price']
        # Somente salvar se houve mudança de preco
        if precoAtual != precoAnterior:
                add_item_history(item)
                update_item(item) 

        # Não salvar se preço for 0
        if precoAtual <= 0:
                return False, 0
        elif precoAtual > 0 and precoAnterior == 0:
                aviso_volta_estoque(item)
                return False, 0     

        #if item['oferta'] is not None or precoAtual < precoAnterior:
        if precoAnterior <= 0:
                return False, 0
        if (precoAnterior / precoAtual) - 1  > float(DISCOUNT):
                return True, precoAnterior        

        return False, 0

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

        if data is not None:
                return {
                        'id': data[0],
                        'title': data[1],
                        'price': data[2]
                }
        
        return data

def aviso_volta_estoque(item):
        itemMessage = f"*{item['title']}* \n Está de volta em estoque custando: {item['price']} \n [Clique para acessar]({item['link']})"
        bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')

def remover_precos_duplicados_historico():
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'DELETE FROM wishlist_history WHERE Id not in (select Id from wishlist_history group by ProductId, Price)'
        cursor.execute(aux)
        conn.commit()
        conn.close()

def get_users_to_scrape():
        wishlists = WISHLIST_URL.split(',')
        users = DESTINATION.split(',')

        usersToSend = []
        for i in range(len(wishlists)):
                usersToSend.append({
                        'userId': users[i],
                        'wishlist': wishlists[i]
                })
        return usersToSend

usersToSend = get_users_to_scrape()
wishlist_data_by_user = scraper.get_data(usersToSend)

for wishlist in wishlist_data_by_user:
        for item in wishlist['items']:
                # Executar script se for switch oled
                if item['id'] == 'I3KMIYEAPY0NB5':
                        logging.info(f"Removendo preços duplicados por conter {item['title']} na lista")
                        remover_precos_duplicados_historico()

                sale, precoAnterior = is_on_sale(item)
                #TODO: Controle do que ja foi alertado
                # if sale and item['oferta'] is not None:
                #         logging.info(f"Enviando item {item['title']} em promoção por {item['price']}")
                #         itemMessage = f"# {item['title']} \n Está em oferta Amazon custando: {item['price']}"
                #         bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')
                if sale:
                        logging.info(f"Enviando item {item['title']} voltando em estoque por {item['price']}")
                        itemMessage = f"*{item['title']}* \n Está em promoção custando: ~R${precoAnterior}~ R${item['price']} \n [Clique para acessar]({item['link']})"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='MARKDOWN')

print("Finalizando")