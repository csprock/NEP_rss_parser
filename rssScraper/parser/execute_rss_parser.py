import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))

if __name__ == '__main__': from parsing_utils import make_place_filter, parse_feed, execute_insertions
else: from .parsing_utils import make_place_filter, parse_feed, execute_insertions
from database_utils import connect_to_database, execute_query


parser = argparse.ArgumentParser()

arg_names = ['--password', '--user', '--host', '--dbname', '--url']
help_messages = ['Password for postgres database.', 'user.', 'Host for database', 'Name of database.', 'URL string to database. If specified all other options ignored.']
for arg, help in zip(arg_names, help_messages):
    parser.add_argument(arg, help = help)


def execute(**kwargs):

    if 'url' in kwargs:
        conn = connect_to_database(url = kwargs['url'])
    else:
        conn = connect_to_database(dbname = kwargs['dbname'], password = kwargs['password'], host = kwargs['host'], user = kwargs['user'])

    # query string for selecting list of market_id's
    q1 = '''
         SELECT market_id FROM media_markets WHERE market_id
         IN (SELECT DISTINCT(places.market_id) FROM places)
         '''

    # query string for selecting feed_id and RSS url for publishers in a media market specified by market_id
    # publishers with no URL are excluded
    q2 = '''
         SELECT feed_id, url FROM publishers INNER JOIN feeds ON publishers.pub_id = feeds.pub_id
         WHERE market_id = %s AND url IS NOT NULL
         '''

    # get list of market_id's
    markets = execute_query(conn, q1, data = None, return_values = True)

    # given media market, cycle through all publishers and feeds
    for m_id in markets:

        market_id = m_id[0]

        SG = make_place_filter(conn, market_id)

        feeds = execute_query(conn, query = q2, data = (market_id, ), return_values = True)

        parsed_results = list()
        for f in feeds:
            temp = parse_feed(f[1], f[0], SG)
            if temp is not None:
                parsed_results.extend(temp)

        if parsed_results is not None:
            for r in parsed_results:
                execute_insertions(r, conn)


if __name__ == '__main__':

    args = parser.parse_args()

    if args.url:
        #conn = connect_to_database(url = args.url)
        execute(url = args.url)
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

        #conn = connect_to_database(dbname = dbname, password = password, host = host, user = user)
        execute(dbname = dbname, password = password, host = host, user = user)
