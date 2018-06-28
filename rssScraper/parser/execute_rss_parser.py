import os
import sys
import argparse

parser = argparse.ArgumentParser()

arg_names = ['--password', '--username', '--host', '--dbname', '--url']
help_messages = ['Password for postgres database.', 'Username.', 'Host for database', 'Name of database.', 'URL string to database. If specified all other options ignored.']
for arg, help in zip(arg_names, help_messages):
    parser.add_argument(arg, help = help)

if __name__ == '__main__':

    args = parser.parse_args()

    next_up = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
    sys.path.append(next_up)

    #root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
    #sys.path.append(root_dir)

    from parsing_utils import make_place_filter, parse_feed, execute_insertions
    from database_utils import connect_to_database, execute_query

    if args.url:
        conn = connect_to_database(url = args.url)
    else:
        missing_value_message = "Must specify database {} as environment variable {} or as argument."
        CONN_INFO = dict()


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

    ######################
    # start main program #
    ######################

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
