import os.path
import re
import textwrap
import time

import progressbar as progressbar
import requests

from bs4 import BeautifulSoup


def crawl_link(link):
    return requests.get(link)


def find_next_page_url(html_soup):
    for p in html_soup.find_all('p', {'class': 'sel'}):
        if 'gotoLemmaPrev' in p.find('a')['href']:
            continue
        href = p.find('a')['href']

    tid = re.findall("'([^']*)'", href)[0]
    if tid == 'KA00001':
        return None
    return 'http://www.kruenitz1.uni-trier.de/cgi-bin/getKRArticles.tcl?tid=' + tid


def save_original_article(article, title):
    file_path = get_file_path(title, 'original')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(article.prettify())


def save_processed_article(text, title):
    file_path = get_file_path(title, 'processed')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(title + '\n')
        f.write(textwrap.fill(text, 80))


def get_file_path(title, directory):
    filename = title.replace(' ', '_').replace('=', '_').replace('!', '').replace(',', '').lower()
    dir = directory + '/' if directory else ''
    path_name = './' + dir + filename + '.txt'
    i = 1

    while os.path.isfile(path_name):
        path_name = './' + dir + filename + '_' + str(i) + '.txt'
        i += 1

    return path_name


def handle_article(article):
    title = article.find('em', {'class': 'lemma'}).text

    # TODO: remember last title, if no title exists, append to last title  example biene


    save_original_article(article, title)

    article.find('em', {'class': 'lemma'}).decompose()

    for a in article.find_all('a'):
        a.decompose()

    for span in article.find_all('span', {'class': 'fpage'}):
        span.decompose()

    for span in article.find_all('span', {'class': 'page'}):
        span.decompose()

    text = article.text.strip().lstrip('*').lstrip()

    save_processed_article(text, title)


# 'www.kruenitz1.uni-trier.de/cgi-bin/getKRArticles.tcl?tid=KA00001+opt=1-0+len=+nid=+plen=+prev=+apos=artbegin#KA00001'
link_to_crawl = 'http://www.kruenitz1.uni-trier.de/cgi-bin/getKRArticles.tcl?tid=KA00001'

amount_crawled = 0
bar = progressbar.ProgressBar(maxval=progressbar.UnknownLength)
bar.start()
while link_to_crawl is not None:
    crawled = crawl_link(link_to_crawl)

    soup = BeautifulSoup(crawled.content, 'html.parser')

    link_to_crawl = find_next_page_url(soup)

    for article in soup.find_all('div', {'class': 'article'}):
        handle_article(article)
        time.sleep(0.1)
        bar.update(amount_crawled)
        amount_crawled += 1

bar.finish()
print('\nFinished crawling.\nCrawled {} Articles!'.format(amount_crawled))
