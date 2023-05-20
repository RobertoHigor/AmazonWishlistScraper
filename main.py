import scraper
import telebot
import os
import logging
import data.wishlistData as wishlistData
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WISHLIST_URL = os.environ.get('WISHLIST_URL')
DESTINATION = os.environ.get('DESTINATION')
DISCOUNT = os.environ.get('DISCOUNT').replace(',', '.')

bot = telebot.TeleBot(BOT_TOKEN)

def esta_em_promocao(item, user_id):
        last_item = wishlistData.check_produto_existe(item)
        if last_item is None:
                wishlistData.add_produto(item)
                wishlistData.add_produto_historico(item)
                return False, 0

        preco_atual = item['price']
        precoAnterior = last_item['price']
        # Somente salvar se houve mudança de preco
        if preco_atual != precoAnterior:
                wishlistData.add_produto_historico(item)
                wishlistData.update_produto(item) 

        # Não salvar se preço for 0
        if preco_atual <= 0:
                return False, 0
        elif preco_atual > 0 and precoAnterior <= 0:
                aviso_volta_estoque(item, user_id)
                return False, 0  
        
        # Busca média do preço
        preco_medio = wishlistData.get_preco_medio(item)
        if teve_desconto(precoAnterior, preco_atual, preco_medio):
                return True, precoAnterior        

        return False, 0

def teve_desconto(preco, preco_base, preco_medio):
        return (preco / preco_base) - 1  > float(DISCOUNT) and (preco / preco_medio) - 1  > float(DISCOUNT)

def aviso_volta_estoque(item, user_id):
        itemMessage = f"*{item['title']}* \n Está de volta em estoque custando: {item['price']} \n [Clique para acessar]({item['link']})"
        bot.send_message(user_id, itemMessage, parse_mode='Markdown')

def remover_precos_duplicados_historico():
        sql = 'DELETE FROM wishlist_history WHERE Id not in (select Id from wishlist_history group by ProductId, Price)'
        sqliteData.execute_query(sql)

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

                sale, precoAnterior = esta_em_promocao(item, wishlist['userId'])

                if sale and item['oferta'] is not None:
                        logging.info(f"Enviando item {item['title']} em promoção por {item['price']}")

                        itemMessage = f"\# {item['title']} \n Está em oferta Amazon custando: {item['price']} (desconto de {item['oferta']}%)"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='Markdown')
                elif sale:
                        logging.info(f"Enviando item {item['title']} voltando em estoque por {item['price']}")

                        itemMessage = f"*{item['title']}* \n Está em promoção custando: ~R${precoAnterior}~ R${item['price']} \n [Clique para acessar]({item['link']})"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='Markdown')

print("Finalizando")