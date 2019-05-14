# quote-scraping-game
Guess who this quote I just scraped is from!

## What it does
- Scrapes & saves most popular quotes from Goodreads.com
- Displays quotes and asks you who the author is
- Gives you up to 5 hints based on the metainfo found, including a bio excerpt with redacted names

## Tech
- Scraping with `requests` and `bs4`
- Name recognition with custom "name-essentalization" algorithm & `regex` fuzzy matching

## To run
```
$ python3 -m pip install requests
$ python3 -m pip install bs4
$ python3 -m pip install regex
$ python3 -m pip install termcolor
$ python3 -m pip install pyfiglet
$ python3 main.py
```
