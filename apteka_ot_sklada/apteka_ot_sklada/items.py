from scrapy import Item, Field


class Good(Item):

    timestamp = Field()
    RPC = Field()
    url = Field()
    title = Field()
    marketing_tags = Field()
    brand = Field()
    section = Field()
    price_data = Field()
    stock = Field()
    assets = Field()
    metadata = Field()
