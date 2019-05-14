# quote-scraping-game
Guess who this quote I just scraped is from!

## What it does
- Scrapes & saves most popular quotes from Goodreads.com
- Displays quotes and asks you who the author is
- Gives you up to 5 hints based on the metainfo found, including a bio excerpt with redacted names

## Tech
- Scraping with `requests` and `bs4`
- Name recognition with custom "name-essentalization" algorithm & RegEx fuzzy matching

## To run
`$ python3 main.py`
