import os
import sys


if __name__ == '__main__':

    next_up = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
    sys.path.append(next_up)

    #root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
    #sys.path.append(root_dir)

    from parsing_utils import make_place_filter, parse_feed, execute_insertions
    from database_utils import connect_to_database, connect_to_heroku_database, execute_query, DATABASE_URL


    #conn = connect_to_database(CONN_INFO)
    conn = connect_to_heroku_database(DATABASE_URL)


    q1 = '''
         SELECT market_id FROM media_markets WHERE market_id
         IN (SELECT DISTINCT(places.market_id) FROM places)
         '''

    markets = execute_query(conn, q1, data = None, return_values = True)

    q2 = '''
         SELECT feed_id, url FROM publishers INNER JOIN feeds ON publishers.pub_id = feeds.pub_id
         WHERE market_id = %s AND url IS NOT NULL
         '''

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
