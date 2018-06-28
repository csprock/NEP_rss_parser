import os
import sys
import json
import argparse

parser = argparse.ArgumentParser()

arg_names = ['--password', '--username', '--host', '--dbname', '--url']
help_messages = ['Password for postgres database.', 'Username.', 'Host for database', 'Name of database.', 'URL string to database. If specified all other options ignored.']
for arg, help in zip(arg_names, help_messages):
    parser.add_argument(arg, help = help)


if __name__ == '__main__':

    args = parser.parse_args()
    sys.path.append(os.path.dirname(os.path.realpath('__file__')))

    from database_utils import connect_to_database, execute_query
    from etl_utils import nytScraper, execute_insertions_nyt, generate_dates, execute_api_search

    ########## Setting arguments for session ############

    # define session constants, must be set as environment variables
    API_KEYS = os.environ['API_KEYS'].split(',')
    MARKET_ID = int(os.environ['NYT_MARKET_ID'])
    FEED_ID = int(os.environ['NYT_FEED_ID'])
    RERUN_PATH = os.environ['NYT_RERUN_PATH']

    apiScraper = nytScraper(API_KEYS)

    if args.url:
        conn = connect_to_heroku_database(parser.url)
    else:
        missing_value_message = "Must specify database {} as environment variable {} or as argument."

        if args.password: password = args.password
        elif 'DB_PASSWORD' in os.environ: password = os.environ['DB_PASSWORD']
        else: raise ValueError(missing_value_message.format('password', 'DB_PASSWORD'))

        if args.username: username = args.username
        elif 'DB_USERNAME' in os.environ: username = os.environ['DB_USERNAME']
        else: raise ValueError(missing_value_message.format('user', 'DB_USERNAME'))

        if args.host: host = args.host
        elif 'DB_HOST' in os.environ: host = os.environ['DB_HOST']
        else: raise ValueError(missing_value_message.format('host','DB_HOST'))

        if args.dbname: dbname = args.dbname
        elif 'DB_NAME' in os.environ: dbname = os.environ['DB_NAME']
        else: raise ValueError(missing_Value_message.format('dbname', 'DB_HOST'))

        conn = connect_to_database(dbname = dbname, password = password, host = host, user = username)


    TODAY, YESTERDAY = generate_dates()

    #############################################################################

    # execute any reruns from last session
    with open(RERUN_PATH, 'r') as f:
        to_rerun = json.load(f)

    results, reruns = list(), list()
    if len(to_rerun) > 0:

        for data in to_rerun:

            today = data['date']['today']
            yesterday = data['date']['yesterday']

            old_results, old_reruns = execute_api_search(scraper = apiScraper, place_list = data['place_list'], market_id = MARKET_ID, today = today, yesterday = yesterday)
            results.extend(old_results)
            reruns.extend(old_reruns)


    q = "SELECT place_name, place_id FROM places WHERE market_id = %s"
    place_list = execute_query(conn, q, data = (MARKET_ID, ), return_values = True)

    new_results, new_reruns = execute_api_search(scraper = apiScraper, place_list = place_list, market_id = MARKET_ID, today = TODAY, yesterday = YESTERDAY)

    results.extend(new_results)

    try:
        reruns.append(new_reruns)
        reruns = [r for r in reruns if r != None]   # bugfix for returned None
    except TypeError:
        pass

    # serialize reruns
    with open(RERUN_PATH, 'w') as f:
        json.dump(reruns, f)



    for r_list in results:
        for r in r_list['query_results']:
            execute_insertions_nyt(conn, r, FEED_ID, r_list['place_id'])

    conn.close()
