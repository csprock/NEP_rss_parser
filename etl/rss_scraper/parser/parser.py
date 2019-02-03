import logging
import psycopg2
from queue import Queue
from threading import Thread
from rss_scraper.parser.parsing_utils import parse_feed, make_place_filter, execute_insertions

LOGGER = logging.getLogger('etl.rss_parser')

FEED_INFO_QUERY = '''
    SELECT market_id, feed_id, url
    FROM publishers INNER JOIN feeds
    ON publishers.pub_id = feeds.pub_id
    WHERE url IS NOT NULL;
'''


class RSSWorker(Thread):

    def __init__(self, conn, queue_in, queue_out):
        '''

        Parameters
        ----------
        conn: postgres connection
        queue_in: input job queue
        queue_out: queue the output is to be stored in
        '''

        super(RSSWorker, self).__init__()

        self.conn = conn
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        '''
        Gets job from the queue (market_id, feed_id and url) and
        creates a place filter for that market and then executes
        the RSS parser against that URL.
        '''

        LOGGER.debug("Starting RSS scraping.")

        while True:

            market_id, feed_id, url = self.queue_in.get()
            G = make_place_filter(self.conn, market_id)
            results = parse_feed(url, feed_id, G)

            LOGGER.info("There are {} results for feed {}".format(len(results), feed_id))

            if len(results) > 0:
                [self.queue_out.put(r) for r in results]

            self.queue_in.task_done()


def execute_rss_parser(pg_config):
    '''
    
    Parameters
    ----------
    conn: postgres connection

    Executes RSS parsing cycle, writes results to postgres database
    '''

    conn = psycopg2.connect(**pg_config)

    # get feeds and market ids
    with conn.cursor() as curs:
        curs.execute(FEED_INFO_QUERY)
        feed_info = curs.fetchall()

    LOGGER.debug("There are {} feeds".format(len(feed_info)))

    # create queues
    feed_queue = Queue()
    db_queue = Queue()

    # start workers
    for worker in range(len(feed_info)):
        worker = RSSWorker(conn, feed_queue, db_queue)
        worker.daemon = True
        worker.start()

    # add feeds to queue
    for f in feed_info:
        feed_queue.put(f)

    feed_queue.join()

    LOGGER.debug("Parsing finished, inserting into database")
    # insert results into database
    while not db_queue.empty():
        item = db_queue.get()
        execute_insertions(item, conn)
        db_queue.task_done()

