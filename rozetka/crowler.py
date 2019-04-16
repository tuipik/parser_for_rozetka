import requests
from bs4 import BeautifulSoup
import pprint

# 1. зібрати урли розмірів
# 2. по кожному розміру пройтися по пагінації, зібрати кількість сторінок
# 3. збираємо всі лінки на продукцію
# 4. по кожному лінку проходимо і збираємо ТМ, назву, розмір, матеріал, склад, ціна, наявність
# 5. записуємо в файл

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
    brand = soup.find('div', class_="detail-breadcrums-wrap").\
        find_all('li', class_="breadcrumbs-i ng-star-inserted")[-1].\
        find('span', class_="breadcrumbs-title ng-star-inserted").text.split(' ')[2:]
    item_brand = ' '.join(brand)

    item_name = soup.find('div', class_="detail-title-code pos-fix clearfix").\
        find('h1', class_="ng-star-inserted").text

    item_price = int(soup.find('div', class_="detail-price-lable clearfix").\
        find('div', class_="detail-buy-label ng-star-inserted").text.split()[0])

    return item_brand, item_name, item_price




def main():
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


    for url in all_items_urls:
        print(get_item_info(url))



if __name__ == '__main__':
    main()
