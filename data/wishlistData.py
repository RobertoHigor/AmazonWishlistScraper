import data.sqliteData as sqliteData
from datetime import datetime

def add_produto(item):
        sql = 'INSERT INTO wishlist (id, title, price) VALUES (?, ?, ?)'
        sqliteData.execute_query(sql, (item["id"], item["title"], item["price"]))

def add_produto_historico(item):
        sql = 'INSERT INTO wishlist_history (ProductId, Price, DatePrice) VALUES (?, ?, ?)'
        sqliteData.execute_query(sql, (item["id"], item["price"], datetime.today()))
        
def update_produto(item):
        sql = 'UPDATE wishlist SET price = ? WHERE Id = ?'
        sqliteData.execute_query(sql, (item["price"], item["id"]))

def check_produto_existe(item):
        # TODO: Fechar conexão com ContexLib
        sql = 'SELECT Id, Title, Price FROM wishlist WHERE Id = ?'
        data = sqliteData.query_first(sql, (item["id"], ))

        if data is not None:
                return {
                        'id': data[0],
                        'title': data[1],
                        'price': data[2]
                }
        
        return data

def get_preco_medio(item):
        sql = 'SELECT AVG(Price) FROM wishlist_history WHERE ProductId = ?'
        data = sqliteData.query_first(sql, (item["id"],))  
        return data[0]