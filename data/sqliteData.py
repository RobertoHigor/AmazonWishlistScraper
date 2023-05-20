import sqlite3

def create_connection():
    return sqlite3.connect('wishlist.sqlite')
  
def execute_query(sql, parameters=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    conn.commit()
    conn.close()

def query_first(sql, parameters=None):
    conn = create_connection()
    cursor = conn.cursor()
    data = cursor.execute(sql, parameters).fetchone()
    conn.close()
    return data

   