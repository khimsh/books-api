import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import lxml
from csv import writer
import time

intelekti_url = 'https://intelekti.ge/books_ge.php?id=235&show='


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


def get_intelekti_books(url: str):
    '''
    Parse artanuji.ge and return book name, author, price, isbn, url
    '''
    try:
        html = get_raw_html(url)
        soup = BeautifulSoup(html, 'lxml').find(
            'ul', {'class': 'booklist'}).find_all('li')
    except TypeError:
        print(f'a typeError error has occured')
        return

    return soup


with open('books_intelekti.csv', 'w', encoding='utf-8', newline='') as csv_file:
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
        intelekti_books = get_intelekti_books(intelekti_url + str(page_num))
        page_num = page_num + 30

        for book in intelekti_books:
            source = 'ინტელექტი'
            book_rel_url = book.find('a')['href']
            book_abs_url = 'https://intelekti.ge/' + book_rel_url

            raw_html = get_raw_html(book_abs_url)
            soup = BeautifulSoup(raw_html, 'lxml').find(
                'div', {'class': 'book_info'})
            book_cover = 'https://intelekti.ge/' + soup.find('img')['src']
            title = soup.find('div', {'class': 'book_name'}).text
            author = soup.find('div', {'class': 'authors_name'}).text
            isbn = soup.find('dl', {'class': 'book_specs'}).find('dd').text
            price = soup.find('dl', {'class': 'book_specs'}
                              ).find_all('dd')[-1].text.split(' ')[0]

            csv_writer.writerow([
                source,
                title,
                author,
                book_abs_url,
                isbn,
                price,
                book_cover
            ])
            time.sleep(1)
        if len(intelekti_books) < 1:
            iterate = False
