import re
from functools import wraps
from time import sleep

import requests
from bs4 import BeautifulSoup

from classes.BadQuoteError import BadQuoteError


SITE = 'https://www.goodreads.com'


def bounce_bad_quote(fn):
  """Raise `BadQuoteError` if `fn` returns junk, else return result unchanged"""
  @wraps(fn)
  def wrapper(*args, **kwargs):
    result = fn(*args, **kwargs)
    if not result or result == 'None':
      raise BadQuoteError
    return result
  return wrapper


# ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ TOPICS ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓


def get_topics():
  pass


# ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ QUOTES ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓


@bounce_bad_quote
def extract_text(quote):
  text = ''
  for char in quote.find(class_="quoteText").get_text().strip():
    text += char
    if char == '”':
      break
  return text

@bounce_bad_quote
def extract_author_name(quote):
  return quote.find(class_='authorOrTitle').get_text().strip(', \t\n')

@bounce_bad_quote
def extract_author_href(quote):
  """See if quote contains valid link to author description, and return that if so"""
  author_href = quote.a['href']
  return author_href if author_href[-4:] != '.jpg' else None

def extract_next_page_href(soup):
  try:
    return soup.find(class_='next_page')['href']
  except KeyError:
    return None


def dictify(quotes_raw):
  """Turn list of HTML blocks into list of neatly ordered dicts"""
  quotes = []
  for quote in quotes_raw:
    try:
      quotes.append({
        'text': extract_text(quote),
        'author_name': extract_author_name(quote),
        'author_href': extract_author_href(quote)
        })
    except:
      continue
  return quotes


def get_quotes(crawl_delay=1, crawl_stop=None):
  """Scrape all quotes+metadata from `SITE` for given topic and return as list of dicts"""
  url = SITE + '/quotes?page=1'
  quotes_raw = []
  while True:
    print(f'Scraping {url} for quotes...')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_raw += soup.find_all(class_='quoteDetails')
    if crawl_stop and f'page={crawl_stop}' in url:
      break
    next_page_href = extract_next_page_href(soup)
    if not next_page_href:
      break
    url = SITE + next_page_href
    sleep(crawl_delay)
  quotes = dictify(quotes_raw)
  return quotes


# ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ QUOTE DETAILS (goodreads.com) ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓


@bounce_bad_quote
def extract_author_born_date(soup):
  return soup.find(itemprop='birthDate').get_text().strip()

@bounce_bad_quote
def extract_author_born_location(response):
  lines = response.text.split('\n')
  line_after = [line for line in lines if 'birthDate' in line][0]
  index_after = lines.index(line_after)
  return lines[index_after-1].strip()

@bounce_bad_quote
def extract_author_description(soup, author_id):
  description = soup.find(id=f'freeTextauthor{author_id}')
  formatted = str(description).replace('\n', '').replace('<br/><br/>', '\n')
  soup = BeautifulSoup(formatted, 'html.parser')
  return soup.get_text()


def get_quote_details(author_href):
  """Scrape author details from `SITE` for given quote and return as dict"""
  url = SITE + author_href
  response = requests.get(url)
  author_id = re.search(r'(?<=/)(\d+)(?=\.)', author_href).group()
  soup = BeautifulSoup(response.text, 'html.parser')
  return {
    'author_born_date': extract_author_born_date(soup),
    'author_born_location': extract_author_born_location(response),
    'author_description': extract_author_description(soup, author_id)
  }

# ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ QUOTE DETAILS (wikipedia.org) ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓

# TODO
