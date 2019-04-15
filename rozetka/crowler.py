import requests
from bs4 import BeautifulSoup
import pprint

# 1. зібрати урли розмірів
# 2. по кожному розміру пройтися по пагінації, зібрати кількість сторінок
# 3. збираємо всі лінки на продукцію
# 4. по кожному лінку проходимо і збираємо ТМ, назву, розмір, матеріал, склад, ціна
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



def main():
    base_url = ["https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013629",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013601",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013279",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013426",
                "https://rozetka.com.ua/ua/search/?class=0&text=%D0%BA%D0%BE%D0%BB%D0%B3%D0%BE%D1%82%D0%BA%D0%B8&section_id=4654655&option_val=1013468",
                ]

    all_paginated_pages = []
    for url in base_url:
        for i in range(1, get_total_pages(get_html(url))+1):
            generated_url = url + '&p=' + str(i)
            all_paginated_pages.append(generated_url)


if __name__ == '__main__':
    main()
