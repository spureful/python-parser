import logging

import collections
import csv
import requests
import bs4

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParsedResult',
    (
        'brand_name',
        'goods_name',
        'url',
        'price_value'
    )
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
    'Цена'
)

class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64;rv: 86.0) Gecko / 20100101Firefox / 86.0',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5en;q=0.3'
        }
        self.result = []

    def load_page(self):
        url = 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/platya'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):

        url_block = block.select_one('a.ref_goods_n_p')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('not url')
            return

        brand_name = block.select_one('strong.brand-name.c-text-sm')
        if not brand_name:
            logger.error('no brand_name')
            return
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = block.select_one('span.goods-name')
        if not goods_name:
            logger.error('no good_name')
            return
        goods_name = goods_name.text.strip()

        price_value = block.select_one('ins.lower-price')
        if not price_value:
            logger.error('no price_value')
            return
        price_value = price_value.text
        price_value = price_value.replace('\u20bd', '').strip()

        logger.debug('%s, %s, %s, %s', url, brand_name, goods_name, price_value)

        self.result.append(ParseResult(
            brand_name=brand_name,
            goods_name=goods_name,
            url=url,
            price_value=price_value
        ))

    def save_result(self):
        path = 'F:/WEB/практика/python_parser-wb/wb/test.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'recieve {len(self.result)} elements')
        self.save_result()

if __name__ == '__main__':
    parser = Client()
    parser.run()