import requests
from bs4 import BeautifulSoup
from time import sleep


def get_quotes():
  """Called by scrape_or_load() to scrape quote blocks from all pages on website.
  Extracts their info to a list of dicts.
  Passes list to _save_to_csv() for saving and also returns it."""
  url = 'http://quotes.toscrape.com/page/1/'
  quotes_raw = []
  while True:
    print(f'Scraping {url} for quotes...')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_raw += soup.find_all(class_='quote')
    try:
      url = 'http://quotes.toscrape.com' + soup.find(class_='next').a['href']
    except AttributeError:
      break
    sleep(1)
  quotes = [{
    'text': quote.find(class_="text").get_text(),
    'author': quote.find(class_="author").get_text(),
    'href': 'http://quotes.toscrape.com' + quote.a['href']
  } for quote in quotes_raw]
  return quotes

def get_details(url):
  """Called by _pick_quote() to scrape current quote's subpage and return additional details."""
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  return {
    'author_born_date': soup.find(class_="author-born-date").get_text(),
    'author_born_location': soup.find(class_="author-born-location").get_text(),
    'author_description': soup.find(class_="author-description").get_text()
  }
