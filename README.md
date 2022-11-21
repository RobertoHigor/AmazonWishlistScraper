# Amazon Wishlist Scraper

This project is based on [jcapona scrapper](https://github.com/jcapona/amazon-wishlist-scraper)

## Github secrets:

- BOT_TOKEN = Telegram BOT Token
- WISHLIST_URL = Amazon wishlist url (viewType=list)
- DESTINATION = Telegram chat id to send alerts
- DISCOUNT = % de desconto em fração. ex: 0.15 para 15%
Usage:

```sh
$ python main.py <<AMAZON WISHLIST URL>>
```

## Links uteis

Formatação de mensagem
https://core.telegram.org/bots/api#markdownv2-style