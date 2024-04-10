from bs4 import BeautifulSoup
import requests
import dateutil.parser as dateParser
import argparse

parser = argparse.ArgumentParser(
    prog='Mashable Crawler',
    description="A script to scrape Mashable",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument("-p", "--pages", type=int, help="number of pages to crawl")
parser.add_argument("-a", "--api", type=str, help="the url to submit data to")
parser.add_argument("-s", "--secret", type=str, help="secret for the api")
args = parser.parse_args()

if not args.api:
    raise Exception('--api is a required argument')

if not args.secret:
    raise Exception('--secret is a required argument')

api_url = args.api
parser_secret = args.secret
pages = args.pages if args.pages else 586

headers = { 
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", 
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
} 

main_url = 'https://sea.mashable.com/article'
LINE_CLEAR = '\x1b[2K'
MOVE_TO_START = '\r'

def getMoreArticlesUrl(page):
    return f'https://sea.mashable.com/?page={page}'

def parseArticles(url):
    response = requests.get(url, headers=headers)
    page = BeautifulSoup(response.text, 'lxml')
    articles_block = page.find('div', attrs={ 'id': 'new' })
    article_card = articles_block.find_all('li', attrs={ 'class': 'blogroll ARTICLE'})

    data = []

    for card in article_card:
        link = card.find('a')
        info_block = card.find('div', attrs={ 'class': 'broll_info'})
        caption = info_block.find('div', attrs={ 'class', 'caption' })
        date = info_block.find('time', attrs={ 'class': 'datepublished' })
        parsed_date = dateParser.parse(date.text)
        iso_date = parsed_date.isoformat()

        data.append({
            'title': caption.text,
            'published_date': iso_date,
            'link': link['href'],
        })

    return data

def printParsingStatus(num_page, num_article):
    print(end=LINE_CLEAR)

    if num_page < pages:
        print(f'Parsing in progress. Number of page parsed: {num_page}, Number of article parsed: {num_article}', end=MOVE_TO_START)
    else:
        print(f'Successfully parsed. Number of page parsed: {num_page}, Number of article parsed: {num_article}')

def main():
    printParsingStatus(0, 0)   
    articles = parseArticles(main_url)
    printParsingStatus(1, len(articles))   

    for current_page in range(2, pages + 1):
        url = getMoreArticlesUrl(current_page)
        new_articles = parseArticles(url)
        printParsingStatus(current_page, len(articles))   
        articles.extend(new_articles)

    print('Submitting parsed post to api...', end=MOVE_TO_START)

    requests.post(
        api_url,
        headers={ 'Parser-Secret': parser_secret },
        json=dict(posts=articles)
    )

    print(end=LINE_CLEAR)
    print('Successfully submit parsed post to api')

if __name__ == '__main__':
    main()