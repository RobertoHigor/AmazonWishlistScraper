from model.Wishlist import Wishlist
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

def esta_em_promocao(item:Wishlist, user_id):
        if item.eh_marketplace:
            return False, 0
        
        last_item = wishlistData.check_produto_existe(item.id)
        if last_item is None:
                wishlistData.add_produto(item)
                wishlistData.add_produto_historico(item)
                return False, 0

        preco_anterior = last_item['price']
        # Somente salvar se houve mudança de preco
        if item.price != preco_anterior:
                wishlistData.add_produto_historico(item)
                wishlistData.update_produto(item) 

        # Não salvar se preço for 0
        if item.price <= 0:
                return False, 0
        elif item.price > 0 and preco_anterior <= 0:
                aviso_volta_estoque(item, user_id)
                return False, 0  

        # Busca média do preço
        preco_medio = wishlistData.get_preco_medio(item.id)
        if item.teve_desconto(preco_anterior, preco_medio):
                return True, preco_anterior        

        return False, 0

def aviso_volta_estoque(item:Wishlist, user_id):
        itemMessage = f"*{item.title}* \n Está de volta em estoque custando: {item.price} \n [Clique para acessar]({item.link})"
        bot.send_message(user_id, itemMessage, parse_mode='Markdown')


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
        item:Wishlist
        if not wishlist['items']:
                bot.send_message(wishlist['userId'], 'Lista vazia. Verificar bot', parse_mode='Markdown')
                
        for item in wishlist['items']:
                # Executar script se for switch oled
                if item.id == 'I3KMIYEAPY0NB5':
                        logging.info(f"Removendo preços duplicados por conter {item.title} na lista")
                        wishlistData.remover_precos_duplicados_historico()

                sale, precoAnterior = esta_em_promocao(item, wishlist['userId'])

                if sale and item.oferta is not None:
                        logging.info(f"Enviando item {item.title} em oferta por {item.price}")

                        itemMessage = f"\# {item.title} \n Está em oferta Amazon custando: {item.price} (desconto de {item.oferta}%)"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='Markdown')
                elif sale:
                        logging.info(f"Enviando item {item.title} em promoção por {item.price}")

                        itemMessage = f"*{item.title}* \n Está em promoção custando: ~R${precoAnterior}~ R${item.price} \n [Clique para acessar]({item.link})"
                        bot.send_message(wishlist['userId'], itemMessage, parse_mode='Markdown')

print("Finalizando")