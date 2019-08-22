import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import lxml
from csv import writer

artanuji_url = 'https://www.artanuji.ge/books_ge.php'


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

    return raw_html


def get_artanuji_books(url: str):
    '''
    Parse artanuji.ge and return book name, author, price, isbn, url
    '''
    try:
        html = get_raw_html(url)
        soup = BeautifulSoup(html, 'lxml').find_all(
            'div', {'class': 'book-category-textarea'})
    except HTTPError as http_err:
        print(f'HTTP error has occured: {http_err}')

    return soup


def get_artanuji_book_covers(url: str):
    '''
    Parse artanuji.ge for book covers
    '''
    try:
        html = get_raw_html(url)
        soup = BeautifulSoup(html, 'lxml').find_all(
            'div', {'class': 'book_list_left'})
    except HTTPError as http_err:
        print(f'HTTP error has occured: {http_err}')

    return soup


artanuji_books = get_artanuji_books(artanuji_url)
artanuji_covers = get_artanuji_book_covers(artanuji_url)


with open('books_artanuji.csv', 'w', encoding='utf-8', newline='') as csv_file:
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

    for book in artanuji_books:
        source = 'არტანუჯი'
        title = book.find('h3').find('a')
        author = book.find('h4').find('a').text
        book_rel_url = title['href']
        book_abs_url = 'https://www.artanuji.ge/' + book_rel_url
        book_data = book.find('div', {'class': 'book-data'}).find_all('p')
        isbn = book_data[0].find('span').next_sibling.strip()
        price = book_data[-1].find('span').next_sibling.strip()
        for cover in artanuji_covers:
            a = cover.find('a')
            if a['href'] == book_rel_url:
                book_cover = a.find('img')['data-original']
                book_cover = 'https://www.artanuji.ge/' + book_cover

        csv_writer.writerow([
            source,
            title.text,
            author,
            book_abs_url,
            isbn,
            price,
            book_cover
        ])
