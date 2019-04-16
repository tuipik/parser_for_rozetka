import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime
from multiprocessing import Pool
import pprint

# 1. зібрати урли розмірів
# 2. по кожному розміру пройтися по пагінації, зібрати кількість сторінок
# 3. збираємо всі лінки на продукцію
# 4. по кожному лінку проходимо і збираємо ТМ, назву, розмір, матеріал, склад, ціна, наявність
# 5. записуємо в файл
# 6. багатопоточність

def get_html(url):
    '''отримуємо весь базовий html'''
    r = requests.get(url)
    return r.text


def get_total_pages(html):
    '''перевіряємо пагінацію і повертаємо кількість сторінок'''
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('ul', class_="clearfix inline paginator-catalog").\
        find_all('a', class_="novisited paginator-catalog-l-link")[-1].get('href')
    total_pages = pages.split('&p=')[-1]
    return int(total_pages)


def get_item_urls(html):
    '''збираємо всі посилання на товари'''
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find('div', class_="g-i-tile-l clearfix").\
        find_all('a', class_="responsive-img centering-child-img")
    items_urls = [i.get('href') for i in items]
    return items_urls


def get_item_info(html):
    '''збираємо інформацію про товар'''
    soup = BeautifulSoup(html,'lxml')

    try:
        brand = soup.find('div', class_="detail-breadcrums-wrap").\
            find_all('li', class_="breadcrumbs-i ng-star-inserted")[-1].\
            find('span', class_="breadcrumbs-title ng-star-inserted").\
                    text.split(' ')[2:]
        item_brand = ' '.join(brand)
    except AttributeError:
        item_brand = 'Виробника не знайдено'


    try:
        item_name = soup.find('div', class_="detail-title-code pos-fix clearfix").\
            find('h1', class_="ng-star-inserted").text
    except AttributeError:
        item_name = 'Назву не знайдено'


    try:
        item_price = int(
            soup.find('div', class_="detail-price-lable clearfix").\
                find('div', class_="detail-buy-label ng-star-inserted").\
                text.split()[0])
    except AttributeError:
        try:
            item_price = int(
                soup.find('div', class_="detail-main-wrap clearfix").find(
                    'div', class_="detail-price-uah").text.split()[0])
        except AttributeError:
            item_price = 0


    try:
        availability = soup.find('div', class_="price_cart").\
            find('div', class_='detail-status').text.strip()
    except AttributeError:
        availability = 'Є в наявності'

    item_info = {'Виробник': item_brand,
                'Назва': item_name,
                'Ціна': item_price,
                'Наявність': availability,
                }

    # iterating tables with item data
    for tab in soup.find_all('table',
                             attrs={'class': ['feature-t ng-star-inserted']}):
        for row in tab.find_all('tr'):
            tmp = row.find_all('td')
            if len(tmp) == 2:
                item_info[re.sub(r'\s{3,}', '', tmp[0].text.strip())] = \
                    re.sub(r'\s{3,}', '', tmp[1].text.strip())


    return item_info


def write_csv(data):
    with open('kolgotki.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('Виробник', 'Назва', 'Зріст', 'Ціна', 'Наявність',
                         'Матеріал', 'Склад', 'Сезон'))
        try:
            for row in data:
                writer.writerow((row['Виробник'],
                                 row['Назва'],
                                 row['Зріст'],
                                 row['Ціна'],
                                 row['Наявність'],
                                 row['Склад']))
        except KeyError:
            pass


def make_all(url):
    # item_url = get_item_urls(get_html(url))
    # print(item_url)

    a = get_item_info(get_html(url))
    return a

def main():
    start = datetime.now()
    base_url = ["https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013629",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013601",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013279",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013426",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013468",
                ]

    all_paginated_pages = []    # Збираємо до купи всі сторінки з пагінації
    for url in base_url:
        for i in range(1, get_total_pages(get_html(url))+1):
            generated_url = url + '&p=' + str(i)
            all_paginated_pages.append(generated_url)


    all_items_urls = []     # Збираємо до купи всі посилання на товари
    for page in all_paginated_pages:
        all_items_urls += get_item_urls(get_html(page))
    all_items_urls = set(all_items_urls)    # прибираємо повтори
    print(len(all_items_urls))
    # all_items_urls = ['https://rozetka.com.ua/ua/legka_hoda_4823028072820/p22136472/',
    #                   'https://rozetka.com.ua/ua/giulia_4820040937342/p47649128/',
    #                   'https://rozetka.com.ua/ua/zeki_corap_roz62050119589/p37261912/',
    #                   'https://rozetka.com.ua/ua/legka_hoda_4823028081020/p35883153/']
    # all_items_info = []
    # for url in all_items_urls:
    #     all_items_info.append(get_item_info(get_html(url)))


    with Pool(40) as p:
        asd = p.map(make_all, all_items_urls)
        print(len(asd))
        pprint.pprint(asd)

        # print(a)
        # all_items_info.append(a)

    # pprint.pprint(all_items_info)
    print(len(asd))
    write_csv(asd)

    end = datetime.now()
    print(end - start)

if __name__ == '__main__':
    main()


# 0:00:00.761059