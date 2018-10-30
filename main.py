import os
from csv import DictReader, DictWriter
from random import choice

from pyfiglet import figlet_format
from termcolor import colored

import scraper
from classes.BadQuoteError import BadQuoteError


def _give_hint(i, quote):
  """Called by play_round() to return ith hint for quote."""
  author_first = quote['author_name'].split(' ')[0]
  author_last = quote['author_name'].split(' ')[-1]
  author_description_redacted = quote['author_description'].replace(quote['author_name'], 'REDACTED REDACTED').replace(author_first, 'REDACTED').replace(author_last, 'REDACTED')
  hints = [
    colored("\nGuess who this quote is from", attrs=['underline']) + f":\n{quote['text']}",
    colored("Hint", attrs=['underline']) + f": the author was born on {quote['author_born_date']} {quote['author_born_location']}!",
    colored("Hint", attrs=['underline']) + f": the author's first name begins with the letter '{author_first[0]}'!",
    colored("Hint", attrs=['underline']) + f": the author's last name begins with the letter '{author_last[0]}'!",
    colored("Hint", attrs=['underline']) + f": here's some more stuff about the author...\n{author_description_redacted}",
  ]
  return hints[i]

def _save_to_csv(quotes):
  """Called by scrape_or_load() to save quotes to CSV file."""
  with open('quotes.csv', 'w') as file:
    DW_object = DictWriter(file, fieldnames=quotes[0].keys())
    DW_object.writeheader()
    DW_object.writerows(quotes)

def _load_from_csv():
  """Called by scrape_or_load() to return saved quotes from CSV file."""
  with open('quotes.csv') as file:
    DR_object = DictReader(file)
    return [row for row in DR_object]

def _pick_quote(quotes):
  """Called by play_round() to select random quote and update it with extra details using scraper.get_quote_details()."""
  quote = quotes.pop(choice(range(len(quotes)))) # popped-off quotes reapper on scrape_or_load()
  try:
    quote.update(scraper.get_quote_details(quote['author_href']))
    return quote, quotes
  except:
    return _pick_quote(quotes)

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

def play_round(quotes, total_guesses):
  """Selects a quote using _pick_quote().
  Conducts a round of the game using _give_hint()."""
  os.system('clear')
  print(f"Number of remaining quotes: {len(quotes)}")
  quote, quotes = _pick_quote(quotes)
  for i in range(total_guesses):
    print(_give_hint(i, quote))
    guess = input(colored("Your guess: ", attrs=['bold']))
    if guess.lower().replace(" ", "") == quote['author_name'].lower().replace(" ", ""):
      print(colored("\nYou win!", 'magenta', attrs=['bold']))
      break
    elif i < total_guesses-1:
      print(f"\nThat's not the one. {total_guesses-1-i} guesses left!")
    else:
      print(colored("\nSorry, you lose!", 'red') + f"\n(The author is {quote['author_name']}.)")
  return quotes

def scrape_or_load():
  """Asks user if they want to scrape web or load from CSV.
  Calls scraper.get_quotes() or _load_from_csv() accordingly."""
  if not os.path.exists('quotes.csv'):
    quotes = scraper.get_quotes()
    _save_to_csv(quotes)
    return quotes
  wants_to_scrape = input("Would you like to scrape the web to update your quotes before playing? (y/n) ")
  if wants_to_scrape[0].lower() not in 'yn':
    return scrape_or_load()
  if wants_to_scrape[0].lower() == 'y':
    quotes = scraper.get_quotes()
    _save_to_csv(quotes)
    return quotes
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
    if quotes == []:
      print(colored("\nALL OUT OF QUOTES.", attrs=['bold']))
      break
    wants_to_play = ask_to_play()
  print("\nThanks for playing, bye!\n")

if __name__ == '__main__':
  main()
