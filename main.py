import argparse

from nytScraper.execute_nyt_scraper import execute as nyt_execute
from rssScraper.parser.execute_rss_parser import execute as rss_execute

parser = argparse.ArgumentParser()

arg_names = ['--password', '--user', '--host', '--dbname', '--url']
help_messages = ['Password for postgres database.', 'user.', 'Host for database', 'Name of database.', 'URL string to database. If specified all other options ignored.']
for arg, help in zip(arg_names, help_messages):
    parser.add_argument(arg, help = help)

args = parser.parse_args()

if args.url:
    print("Starting RSS parser....")
    rss_execute(url = args.url)
    print("Starting NYT API scraper....")
    nyt_execute(url = args.url)
else:
    missing_value_message = "Must specify database {} as environment variable {} or as argument."
    CONN_INFO = dict()

    if args.password: password = args.password
    elif 'DB_PASSWORD' in os.environ: password = os.environ['DB_PASSWORD']
    else: raise ValueError(missing_value_message.format('password', 'DB_PASSWORD'))

    if args.user: user = args.user
    elif 'DB_user' in os.environ: user = os.environ['DB_user']
    else: raise ValueError(missing_value_message.format('user', 'DB_user'))

    if args.host: host = args.host
    elif 'DB_HOST' in os.environ: host = os.environ['DB_HOST']
    else: raise ValueError(missing_value_message.format('host','DB_HOST'))

    if args.dbname: dbname = args.dbname
    elif 'DB_NAME' in os.environ: dbname = os.environ['DB_NAME']
    else: raise ValueError(missing_Value_message.format('dbname', 'DB_HOST'))

    print("Starting RSS parser....")
    rss_execute(dbname = dbname, user = user, password = password, host = host)
    print("Starting NYT API scraper....")
    nyt_execute(dbname = dbname, user = user, password = password, host = host)
