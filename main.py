import os
import unicodedata
from csv import DictReader, DictWriter
from random import choice
from time import sleep

import regex
from pyfiglet import figlet_format
from termcolor import colored

import scraper
import ui
from classes.BadQuoteError import BadQuoteError


PRINT_DELAY = 1
CRAWL_DELAY = 1


def essentialize(full_name):
  """Return the "essence" of a person's name, for fair comparison
  
  - strip whitespace, make lower case
  - remove any middle names
  - remove punctuation & accents (diacritical marks)
  Examples:
  (1) `'  Emily Jane Brontë'` → `'emilybronte'`
  (2) `'J.R.R. Tolkien'` → `'jtolkien'`
  """
  names = full_name.strip().lower().replace('.', '. ').split(' ')
  no_middle = names[0]
  if len(names) > 1:
    no_middle += names[-1]
  no_punctuation = ''.join(char for char in no_middle if char not in " '.-")
  no_accents = unicodedata.normalize('NFKD', no_punctuation).encode('ASCII', 'ignore').decode()
  return no_accents

def is_fuzzy_match(a, b):
  """Return `True` if string `a` is "basically the same" as string `b`, else `False`
  
  - fuzzy string matching
  - allows 1 mistake for every 6 characters in `a`, but at least 1
  - mistake may be insertion, deletion, or substitution
  """
  fuzzlimit = round(len(a)/6) or 1
  fuzzy = fr'(?:{b}){{i,d,s,e<={fuzzlimit}}}'
  return bool(regex.fullmatch(fuzzy, a))

def redact_author_description(author_description, author_name):
  """Return text with all appearences of author's name replaced with name-length blocks of `'█'`"""
  for name in author_name.split(' '):
    author_description = author_description.replace(name, '█'*len(name))
  return author_description

def _give_hint(i, quote):
  """Return `i`th hint for given quote."""
  author_first = quote['author_name'].split(' ')[0]
  author_last = quote['author_name'].split(' ')[-1]
  author_description_redacted = redact_author_description(quote['author_description'], quote['author_name'])
  hints = [
    colored("\nGuess who this quote is from", attrs=['underline']) + f":\n{ui.format_text_block(quote['text'])}",
    colored("Hint", attrs=['underline']) + f": the author was born on {quote['author_born_date']} {quote['author_born_location']}!",
    colored("Hint", attrs=['underline']) + f": the author's first name begins with the letter '{author_first[0]}'!",
    colored("Hint", attrs=['underline']) + f": the author's last name begins with the letter '{author_last[0]}'!",
    colored("Hint", attrs=['underline']) + f": here's some more stuff about the author...\n\n{ui.format_text_block(author_description_redacted)}\n",
  ]
  return hints[i]

def _scrape_and_save():
  quotes = scraper.get_quotes(crawl_delay=CRAWL_DELAY, crawl_stop=10)
  _save_to_csv(quotes)
  return quotes

def _save_to_csv(quotes):
  with open('quotes.csv', 'w') as file:
    DW_object = DictWriter(file, fieldnames=quotes[0].keys())
    DW_object.writeheader()
    DW_object.writerows(quotes)

def _load_from_csv():
  with open('quotes.csv') as file:
    DR_object = DictReader(file)
    return [row for row in DR_object]

def _pick_quote(quotes):
  """Return random quote updated with author details, or `None` if details are N/A"""
  quote = quotes.pop(choice(range(len(quotes))))
  try:
    quote.update(scraper.get_quote_details(quote['author_href']))
    return quote, quotes
  except:
    sleep(CRAWL_DELAY)
    return None, quotes

def ask_to_play():
  """Ask user to play again, and return `True` or `False` depending on answer"""
  wants_to_play = input("\nWould you like to keep playing? (y/n) ")
  if not wants_to_play or wants_to_play[0].lower() not in 'yn':
    return ask_to_play()
  if wants_to_play[0].lower() == 'y':
    return True
  return False

def enforce_working_directory():
  """Sets working directory to the folder this .py file is in"""
  os.chdir(os.sys.path[0])

def play_round(quotes, total_guesses):
  """Selects a quote using _pick_quote().
  Conducts a round of the game using _give_hint()."""
  quote = {}
  while not quote:
    quote, quotes = _pick_quote(quotes)
    os.system('clear')
    print(f"Number of remaining quotes: {len(quotes)}")
  sleep(PRINT_DELAY)
  for i in range(total_guesses):
    print(_give_hint(i, quote))
    guess = input(colored("Your guess: ", attrs=['bold']))
    if is_fuzzy_match(essentialize(guess), essentialize(quote['author_name'])):
      print(colored("\nYou win!", 'magenta', attrs=['bold']))
      sleep(PRINT_DELAY)
      break
    elif i < total_guesses-1:
      print(f"\nThat's not the one. {total_guesses-1-i} guesses left!")
    else:
      print(colored("\nSorry, you lose!", 'red'), end='')
      sleep(PRINT_DELAY)
      print(f" (The author is {quote['author_name']}.)")
    sleep(PRINT_DELAY)
  return quotes

def scrape_or_load():
  """Scrape web for quotes or load them from CSV

  - scrape without asking if there's no CSV
  - user can choose otherwise
  """
  if not os.path.exists('quotes.csv'):
    return _scrape_and_save()
  wants_to_scrape = input("Would you like to scrape the web to update your quotes before playing? (y/n) ")
  if not wants_to_scrape or wants_to_scrape[0].lower() not in 'yn':
    return scrape_or_load()
  if wants_to_scrape[0].lower() == 'y':
    return _scrape_and_save()
  if wants_to_scrape[0].lower() == 'n':
    return _load_from_csv()


def main():
  os.system('clear')
  print(colored((figlet_format("<  Quote  game  \\>")), 'green', attrs=['bold']))
  enforce_working_directory()
  quotes = scrape_or_load()
  total_guesses = 5 # max.5 unless more hints are added in _give_hint()
  wants_to_play = True
  while wants_to_play:
    quotes = play_round(quotes, total_guesses)
    if quotes:
      wants_to_play = ask_to_play()
    else:
      print(colored("\nALL OUT OF QUOTES.", attrs=['bold']))
      break
  print(colored("\nThanks for playing. Bye!\n", attrs=['bold']))
  sleep(PRINT_DELAY)

if __name__ == '__main__':
  main()
