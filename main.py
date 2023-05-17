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

def esta_em_promocao(item):
        last_item = check_produto_existe(item)
        if last_item is None:
                add_produto(item)
                add_produto_historico(item)
                return False, 0

        preco_atual = item['price']
        precoAnterior = last_item['price']
        # Somente salvar se houve mudança de preco
        if preco_atual != precoAnterior:
                add_produto_historico(item)
                update_produto(item) 

        # Não salvar se preço for 0
        if preco_atual <= 0:
                return False, 0
        elif preco_atual > 0 and precoAnterior == 0:
                aviso_volta_estoque(item)
                return False, 0     

        # Se o preço é <= 0, então ñ está em promoção
        if precoAnterior <= 0:
                return False, 0
        
        # Busca média do preço
        #preco_medio = get_preco_medio(item)
        if teve_desconto(precoAnterior, preco_atual):
                return True, precoAnterior        

        return False, 0

def teve_desconto(preco, preco_base):
        return (preco / preco_base) - 1  > float(DISCOUNT)

def add_produto(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO wishlist (id, title, price) VALUES (?, ?, ?)',
                (item["id"], item["title"], item["price"]))
        conn.commit()
        conn.close()

def add_produto_historico(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'INSERT INTO wishlist_history (ProductId, Price, DatePrice) VALUES ("{item["id"]}", {item["price"]}, datetime("now"))'
        cursor.execute(aux)
        conn.commit()
        conn.close()
        
def update_produto(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        aux = f'UPDATE wishlist SET price = {item["price"]} WHERE Id ="{item["id"]}"'
        cursor.execute(aux)
        conn.commit()
        conn.close()

def check_produto_existe(item):
        # TODO: Fechar conexão com ContexLib
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        data = cursor.execute('SELECT Id, Title, Price FROM wishlist WHERE Id = ?',
                (item["id"], )).fetchone()
        conn.close()

        if data is not None:
                return {
                        'id': data[0],
                        'title': data[1],
                        'price': data[2]
                }
        
        return data

def get_preco_medio(item):
        conn = sqlite3.connect('wishlist.sqlite')
        cursor = conn.cursor()
        data = cursor.execute('SELECT AVG(Price) FROM wishlist_history WHERE ProductId = ?',
                (item["id"],)).fetchone()
        conn.close()        
        return data[0]

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

                sale, precoAnterior = esta_em_promocao(item)
                #TODO: Controle do que ja foi alertado
                # if sale and item['oferta'] is not None:
                #         logging.info(f"Enviando item {item['title']} em promoção por {item['price']}")
                #         itemMessage = f"# {item['title']} \n Está em oferta Amazon custando: {item['price']}"
                #         bot.send_message(DESTINATION, itemMessage, parse_mode='MARKDOWN')
                if sale:
                        logging.info(f"Enviando item {item['title']} voltando em estoque por {item['price']}")
                        itemMessage = f"*{item['title']}* \n Está em promoção custando: ~~R${precoAnterior}~~ R${item['price']} \n [Clique para acessar]({item['link']})"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='MARKDOWN')

print("Finalizando")