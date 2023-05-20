import data.sqliteData as sqliteData
from datetime import datetime

from model.Wishlist import Wishlist

def add_produto(item:Wishlist):
        sql = 'INSERT INTO wishlist (id, title, price) VALUES (?, ?, ?)'
        sqliteData.execute_query(sql, (item.id, item.title, item.price))

def add_produto_historico(item:Wishlist):
        sql = 'INSERT INTO wishlist_history (ProductId, Price, DatePrice) VALUES (?, ?, ?)'
        sqliteData.execute_query(sql, (item.id, item.price, datetime.today()))
        
def update_produto(item:Wishlist):
        sql = 'UPDATE wishlist SET price = ? WHERE Id = ?'
        sqliteData.execute_query(sql, (item.price, item.id))

def check_produto_existe(id):
        # TODO: Fechar conexão com ContexLib
        sql = 'SELECT Id, Title, Price FROM wishlist WHERE Id = ?'
        data = sqliteData.query_first(sql, (id, ))

        if data is not None:
                return {
                        'id': data[0],
                        'title': data[1],
                        'price': data[2]
                }
        
        return data

def get_preco_medio(id):
        sql = 'SELECT AVG(Price) FROM wishlist_history WHERE ProductId = ?'
        data = sqliteData.query_first(sql, (id,))  
        return data[0]

def remover_precos_duplicados_historico():
        sql = 'DELETE FROM wishlist_history WHERE Id not in (select Id from wishlist_history group by ProductId, Price)'
        sqliteData.execute_query(sql)