import os
from nytScraper.execute_nyt_scraper import execute as nyt_execute
from rssScraper.parser.execute_rss_parser import execute as rss_execute

print("Starting RSS parser....")
rss_execute(url = os.environ['DATABASE_URL'])
print("Starting NYT API scraper....")
nyt_execute(url = os.environ['DATABASE_URL'])
