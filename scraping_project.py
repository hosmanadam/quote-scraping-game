# TODO - modify to scrape sites that weren't made to be scraped
# TODO - add unit tests
# TODO - add even more spelling flexibility to guesses


import os
import requests
from random import choice
from bs4 import BeautifulSoup
from time import sleep
from pyfiglet import figlet_format
from termcolor import colored
from csv import DictWriter, DictReader


def _give_hint(i, quote):
  """Called by play_round() to return ith hint for quote."""
  author_first = quote['author'].split(' ')[0]
  author_last = quote['author'].split(' ')[-1]
  author_description_redacted = quote['author_description'].replace(quote['author'], 'REDACTED REDACTED').replace(author_first, 'REDACTED').replace(author_last, 'REDACTED')
  hints = [
    colored("\nGuess who this quote is from", attrs=['underline']) + f":\n{quote['text']}",
    colored("Hint", attrs=['underline']) + f": the author was born on {quote['author_born_date']} {quote['author_born_location']}!",
    colored("Hint", attrs=['underline']) + f": the author's first name begins with the letter '{author_first[0]}'!",
    colored("Hint", attrs=['underline']) + f": the author's last name begins with the letter '{author_last[0]}'!",
    colored("Hint", attrs=['underline']) + f": here's some more stuff about the author...\n{author_description_redacted}",
  ]
  return hints[i]

def _load_from_csv():
  """Called by scrape_or_load() to return saved quotes from CSV file."""
  with open('quotes.csv') as file:
    DR_object = DictReader(file)
    return [row for row in DR_object]

def _pick_quote():
  """Called by play_round() to select random quote and update it with extra details using _scrape_details()."""
  quote = quotes.pop(choice(range(len(quotes)))) # popped-off quotes reapper on scrape_or_load()
  quote.update(_scrape_details(quote['href']))
  return quote

def _save_to_csv(quotes):
  """Called by _scrape_quotes to save quotes to CSV file."""
  with open('quotes.csv', 'w') as file:
    DW_object = DictWriter(file, fieldnames=quotes[0].keys())
    DW_object.writeheader()
    DW_object.writerows(quotes)

def _scrape_details(url):
  """Called by _pick_quote() to scrape current quote's subpage and return additional details."""
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  return {
    'author_born_date': soup.find(class_="author-born-date").get_text(),
    'author_born_location': soup.find(class_="author-born-location").get_text(),
    'author_description': soup.find(class_="author-description").get_text()
  }

def _scrape_quotes():
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
  _save_to_csv(quotes)
  return quotes

def ask_to_play():
  """Asks the user to play again, and returns True or False depending on answer."""
  wants_to_play = input("Would you like to keep playing? (y/n) ")
  if not wants_to_play or wants_to_play[0].lower() not in 'yn':
    return ask_to_play()
  if wants_to_play[0].lower() == 'y':
    return True
  return False

def enforce_working_directory():
  """Sets working directory to the folder this .py file is in"""
  os.chdir(os.sys.path[0])

def play_round():
  """Selects a quote using _pick_quote().
  Conducts a round of the game using _give_hint()."""
  print(f"Number of remaining quotes: {len(quotes)}")
  quote = _pick_quote()
  for i in range(total_guesses):
    print(_give_hint(i, quote))
    guess = input(colored("Your guess: ", attrs=['bold']))
    if guess.lower().replace(" ", "") == quote['author'].lower().replace(" ", ""):
      print(colored("\nYou win!", 'magenta', attrs=['bold']))
      break
    elif i < total_guesses-1:
      print(f"\nThat's not the one. {total_guesses-1-i} guesses left!")
    else:
      print(colored("\nSorry, you lose!", 'red') + f"\n(The author is {quote['author']}.)")

def scrape_or_load():
  """Asks user if they want to scrape web or load from CSV.
  Calls _scrape_quotes() or _load_from_csv() accordingly."""
  if not os.path.exists('quotes.csv'):
    return _scrape_quotes()
  wants_to_scrape = input("Would you like to scrape the web to update your quotes before playing? (y/n) ")
  if not wants_to_scrape or wants_to_scrape[0].lower() not in 'yn':
    return scrape_or_load()
  if wants_to_scrape[0].lower() == 'y':
    return _scrape_quotes()
  if wants_to_scrape[0].lower() == 'n':
    return _load_from_csv()


# GAME LOGIC
print(100*'\n' + colored((figlet_format("<  Quote  game  \\>")), 'green', attrs=['bold']))
enforce_working_directory()
quotes = scrape_or_load()
total_guesses = 5 # max.5 unless more hints are added in _give_hint()
wants_to_play = True
while wants_to_play:
  play_round()
  if quotes == []:
    print(colored("\nALL OUT OF QUOTES.", attrs=['bold']))
    break
  wants_to_play = ask_to_play()
print("\nThanks for playing, bye!\n")