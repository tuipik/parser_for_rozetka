import requests
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool


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


    try:
        link = 'https://rozetka.com.ua' + soup.find('div', class_="nav-tabs-desktop").\
            find('a', class_="nav-tabs-link novisited ng-star-inserted active").\
            get('href')
    except AttributeError:
        availability = 'http'


    item_info = {'Виробник': item_brand,
                'Назва': item_name,
                'Ціна': item_price,
                'Наявність': availability,
                'Матеріал': '',
                'Склад': '',
                'Сезон': '',
                'Посилання': link,
                }

    # Дістаємо інфо з таблиці
    for tab in soup.find_all('table',
                             attrs={'class': ['feature-t ng-star-inserted']}):
        for row in tab.find_all('tr'):
            tmp = row.find_all('td')
            if len(tmp) == 2:
                item_info[re.sub(r'\s{3,}', '', tmp[0].text.strip())] = \
                    re.sub(r'\s{3,}', '', tmp[1].text.strip())


    return item_info


def collect_all_information(url):
    all_information = get_item_info(get_html(url))
    return all_information


def write_csv(data):
    with open('kolgotki_{}.csv'.format(datetime.now()), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('Виробник', 'Назва', 'Зріст', 'Ціна', 'Наявність',
                         'Матеріал', 'Склад', 'Сезон','Посилання'))
        try:
            for row in data:
                writer.writerow((row['Виробник'],
                                 row['Назва'],
                                 row['Зріст'],
                                 row['Ціна'],
                                 row['Наявність'],
                                 row['Склад'],
                                 row['Матеріал'],
                                 row['Сезон'],
                                 row['Посилання'],
                                 ))
        except KeyError:
            pass


def main():
    start = datetime.now()
    base_url = ["https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013629",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013601",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013279",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013426",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013468",
                ]
    print('Починаю шукати по {} запитах'.format(len(base_url)))

    all_paginated_pages = []    # Збираємо до купи всі сторінки з пагінації
    for url in base_url:
        for i in range(1, get_total_pages(get_html(url))+1):
            generated_url = url + '&p=' + str(i)
            all_paginated_pages.append(generated_url)
    print('Знайдено {} сторінок з пошуковими запитами'.format(len(all_paginated_pages)))


    all_items_urls = []     # Збираємо до купи всі посилання на товари
    for page in all_paginated_pages:
        all_items_urls += get_item_urls(get_html(page))
    print('Кількість пошукових запитів - {}'.format(len(all_items_urls)))


    with Pool(50) as p: # Збираємо всю інформацію, яка нас цікавить
        asd = p.map(collect_all_information, all_items_urls)

    write_csv(asd)

    end = datetime.now()
    print('Завершено за {}'.format(end - start))


if __name__ == '__main__':
    main()
