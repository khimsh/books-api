import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import lxml
from csv import writer
from is_isbn.is_isbn import is_isbn

# Entry URL
palitra_url = 'https://www.palitral.ge/tsignebi.html?view=catalog&lang=ka-GE&start='


def get_raw_html(url: str):
    '''
    Return raw html from a given url
    '''
    try:
        response = requests.get(url)
        response.raise_for_status()

        response.encoding = 'utf-8'
        raw_html = response.text
    except HTTPError as http_err:
        print(f'HTTP error has occured: {http_err}')
        return

    return raw_html


def get_palitra_books(url: str):
    try:
        html = get_raw_html(url)
        soup = BeautifulSoup(html, 'lxml').find_all(
            'div', {'class': 'product_item'})
    except TypeError:
        print(f'a typeError error has occured')
        return

    return soup


with open('books_palitra.csv', 'w', encoding='utf-8', newline='') as csv_file:
    csv_writer = writer(csv_file)
    headers = [
        'წყარო',
        'სათაური',
        'ავტორი',
        'აბსოლუტური ლინკი',
        'ISBN',
        'ფასი',
        'ყდა'
    ]
    csv_writer.writerow(headers)

    page_num = 0
    iterate = True
    while iterate:
        palitra_books = get_palitra_books(palitra_url + str(page_num))
        page_num = page_num + 20

        for book in palitra_books:
            source = 'პალიტრა L'
            title = book.find('div', {'class': 'item_titlein'}).find(
                'a').text.strip()
            author = book.find('div', {'class': 'item_author'}
                               ).find('span').next_sibling.strip()
            if len(author) == 0:
                author = 'ავტორი არ არის მითითებული'
            book_cover = book.find(
                'div', {'class': 'ItemImage'}).find('img')['src']
            book_cover = 'https://www.palitral.ge/' + book_cover
            book_abs_url = book.find(
                'div', {'class': 'ItemImage'}).find('a')['href']
            book_abs_url = 'https://www.palitral.ge/' + book_abs_url

            price = book.find('div', {'class': 'item_price'}).find(
                'span').next_sibling.strip().split(' ')[0]
            try:
                # Add only valid ISBN code. If it doesn't exist add string 'None'.
                possible_isbn = book.find('div', {'class': 'item-isbn'}).find(
                    'span').next_sibling.strip()
                isbn = possible_isbn if is_isbn(possible_isbn) else 'None'
            except:
                pass

            csv_writer.writerow([
                source,
                title,
                author,
                book_abs_url,
                isbn,
                price,
                book_cover
            ])
        if len(palitra_books) < 1:
            iterate = False
