import time
from scrapy import Spider, Request

from ..items import Good

# from ..items import Skin

GOODS_PER_PAGE = 12  # количество товаров на одной странице


class GoodsSpider(Spider):
    name = "goods"

    categories = ["kosmetika/bannye-serii/gel-dlya-dusha", "tovary-dlya-mamy-i-malysha/gigiena-malysha/podguzniki-detskie","kontaktnye-linzy-i-ochki/linzy-ezhednevnye"]
    # также город можно установить путем POST запроса на https://apteka-ot-sklada.ru/api/user/city/requestById при старте парсинга
    cookies = {'city': '92'}

    def start_requests(self):
        for category in self.categories:
            yield Request(
                f"https://apteka-ot-sklada.ru/api/catalog/search?sort=popindex&slug={category}&offset=0&limit=12",
                cookies=self.cookies, callback=self.parse_categories, cb_kwargs={"offset": 0, "category": category})

    def parse_categories(self, response, **kwargs):
        goods = response.json().get("goods")
        if goods:
            offset = kwargs["offset"] + GOODS_PER_PAGE
            for good in goods:
                stickers = good["stickers"]
                yield Request(f"https://apteka-ot-sklada.ru/api/catalog/{good['id']}", callback=self.parse_good,
                              cookies=self.cookies, cb_kwargs={"stickers": stickers})
            yield Request(
                f"https://apteka-ot-sklada.ru/api/catalog/search?sort=popindex&slug={kwargs['category']}&offset={offset}&limit=12",
                cookies=self.cookies, callback=self.parse_categories,
                cb_kwargs={"offset": offset, "category": kwargs["category"]})

    def parse_good(self, response, **kwargs):
        data = response.json()
        item = Good()
        item["timestamp"] = time.time()
        item["RPC"] = f'{data["slug"]}_{data["id"]}'
        item["url"] = f"https://apteka-ot-sklada.ru/catalog/{item['RPC']}"
        item["title"] = data["name"]
        item["marketing_tags"] = kwargs["stickers"]
        item["brand"] = data["producer"]
        section = [data["category"]["name"]]
        if data["category"].get("parents"):
            for parent in data["category"]["parents"]:
                section.append(parent["name"])
        item["section"] = section
        discount = (1 - data["cost"] / data["oldCost"]) * 100 if data["cost"] and data["oldCost"] else None
        item["price_data"] = {
            "current": data["cost"],
            "original": data["oldCost"],
            "sale_tag": f'Скидка {discount} %' if discount else None
        }
        item["stock"] = {
            "in_stock": data["inStock"],
            "count": data["availability"]
        }
        item["assets"] = {
            "main_image": data["images"][0],
            "set_images": data["images"],
            "view360": data.get("view360"),
            "video": data.get("videos")
        }

        item["metadata"] = {
            "__description": data["description"],
            "country": data["country"]
        }
        yield item


"""
P.S прокси можно добавить в настройках c помощью ROTATING_PROXIES, но прокси серверов у меня в наличии нет
"""
