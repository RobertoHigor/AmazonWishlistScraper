import math
import os

class Wishlist(object):
    BASE_URL = 'https://www.amazon.com.br'
    DISCOUNT = float(os.environ.get('DISCOUNT').replace(',', '.'))
    def __init__(self, id:str=None, title:str=None, price:float=None, oferta:float=None, link:str=None, eh_marketplace:str=None):
        self.id = id
        self.title = title
        self.price:float = self.try_parse_float(price)
        self.oferta = oferta
        self.link:str = self.BASE_URL + link
        self.eh_marketplace:bool = eh_marketplace is not None

    def try_parse_float(self, num):
        try:
            convertedValue = float(num)
            if math.isinf(convertedValue):
                return 0
            return convertedValue
        except ValueError:
            return 0
        
    def teve_desconto(self, preco_anterior, preco_medio):
        temDesconto = (preco_anterior / self.price ) - 1  > self.DISCOUNT
        menorQueMedia = self.price < preco_medio
        return  temDesconto and menorQueMedia