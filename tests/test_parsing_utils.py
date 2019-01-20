import os
import sys
import unittest
import psycopg2
from datetime import datetime
from copy import copy

if __name__ == '__main__':
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, os.pardir))

from rssScraper.parser.parsing_utils import *
from database_utils import generate_article_query, generate_tag_query, generate_place_mentions_query

# login credentials to database
LOGIN_DB = 'csprock'
TEST_USER = 'csprock'
TEST_HOST = '/var/run/postgresql/'
TEST_DB = 'test_parsing_utils'

# location of database initialization scripts
DATABASE_SCRIPTS = 'test_data'

# load database schema
with open(os.path.join(DATABASE_SCRIPTS, 'schema1.sql')) as f:
    SCHEMA = f.read()

# load database data
with open(os.path.join(DATABASE_SCRIPTS, 'data.sql')) as f:
    DATA = f.read()

class DatabaseInteractionRequired(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # creating connection to login database
        cls.conn = psycopg2.connect(user=TEST_USER,
                                    dbname=LOGIN_DB,
                                    host=TEST_HOST)

        cls.conn.autocommit = True

        # create test database
        with cls.conn.cursor() as curs:
            print("Creating database...")
            curs.execute("DROP DATABASE IF EXISTS {}".format(TEST_DB))
            curs.execute("CREATE DATABASE {}".format(TEST_DB))

        cls.conn.close()

        # connecting to test database
        cls.conn = psycopg2.connect(user=TEST_USER,
                                    dbname=TEST_DB,
                                    host=TEST_HOST)
        cls.conn.autocommit = True

        # seed test database with data
        with cls.conn.cursor() as curs:
            print("Creating schema...")
            curs.execute(SCHEMA)
            print("Creating data...")
            curs.execute(DATA)

        cls.conn.close()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

        cls.conn = psycopg2.connect(user=TEST_USER,
                                    dbname=LOGIN_DB,
                                    host=TEST_HOST)
        cls.conn.autocommit = True

        with cls.conn.cursor() as curs:
            print("Dropping...")
            curs.execute("DROP DATABASE {}".format(TEST_DB))

        cls.conn.close()



# class TestMakePlaceFilter(DatabaseInteractionRequired):
#
#     def setUp(self):
#         self.conn = psycopg2.connect(user=TEST_USER,
#                                      dbname=TEST_DB,
#                                      host=TEST_HOST)
#
#     def tearDown(self):
#         self.conn.close()
#
#     def test_this_class(self):
#
#         with self.conn.cursor() as curs:
#             curs.execute("SELECT * FROM feeds")
#             results = curs.fetchall()
#             print(results)
@unittest.skip("skipping to isolate test")
class TestInfoGenerators(DatabaseInteractionRequired):

    def setUp(self):
        self.conn = psycopg2.connect(user=TEST_USER,
                                     dbname=TEST_DB,
                                     host=TEST_HOST)

        self.G = make_place_filter(self.conn, 1)

    def tearDown(self):

        delattr(self, "G")
        self.conn.close()


    def test_generate_place_mention_in_title(self):

        dummy_parsed_entries_title = {
                'id': None,
                'title': 'Queens is in the title.',
                'link': 'http://dummyurl_1.com',
                'summary': 'there is no place mention here',
                'date': datetime.datetime(year=2018, month=1, day=1)
            }

        results = generate_place_mention_info(dummy_parsed_entries_title, self.G)

        expected = {'place_id': 2,
                    'context': 'Queens is in the title.',
                    'loc': 'title'}

        self.assertDictEqual(results[0], expected)

    def test_generate_place_mention_in_summary(self):

        dummy_parsed_entries_summary = {
            'id': None,
            'title': 'nothing in the title',
            'link': 'http://dummyurl_2.com',
            'summary': 'The first mention of Queens. The second mention of Coney Island.',
            'date': datetime.datetime(year=2018, month=1, day=1)
        }

        expected = [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }
        ]

        results = generate_place_mention_info(dummy_parsed_entries_summary, self.G)

        for i, v in enumerate(expected):
            with self.subTest(i=i):
                self.assertDictEqual(v, results[i])

    def test_generate_place_tag_info(self):

        dummy_place_mention_info = [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }
        ]

        expected = [2, 13]

        results = generate_place_tag_info(dummy_place_mention_info)

        self.assertSetEqual(set(results), set(expected))

    def test_generate_article_info(self):

        dummy_parsed_entries = {
            'id': None,
            'title': 'nothing in the title',
            'link': 'http://dummyurl_2.com',
            'summary': 'The first mention of Queens. The second mention of Coney Island.',
            'date': datetime.datetime(year=2018, month=1, day=1)
        }

        expected = copy(dummy_parsed_entries)
        expected.update({'feed_id': 1})

        result = generate_article_info(dummy_parsed_entries, 1)

        self.assertDictEqual(expected, result)

    def test_generate_info(self):

        dummy_parsed_entries_summary = {
            'id': None,
            'title': 'nothing in the title',
            'link': 'http://dummyurl_2.com',
            'summary': 'The first mention of Queens. The second mention of Coney Island.',
            'date': datetime.datetime(year=2018, month=1, day=1)
        }

        expected_articles = copy(dummy_parsed_entries_summary)
        expected_articles['feed_id'] = 1

        expected_place_tags = [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }
        ]

        expected_place_mentions = [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }
        ]

        expected = {
            'place_tags': [2, 13],
            'place_mentions': expected_place_mentions,
            'articles': expected_articles
        }

        results = get_info(dummy_parsed_entries_summary, 1, self.G)

        self.assertDictEqual(expected, results)
@unittest.skip("skipping to isolate test")
class TestDictionaryMakers(unittest.TestCase):

    def setUp(self):

        self.entry_info = {
            'place_tags': [2, 13],
            'place_mentions': [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }
            ],
            'articles': {
                'id': None,
                'title': 'nothing in the title',
                'link': 'http://dummyurl_2.com',
                'summary': 'The first mention of Queens. The second mention of Coney Island.',
                'date': datetime.datetime(year=2018, month=1, day=1),
            'feed_id': 1
            }
        }

    def test_make_article_dict(self):

        expected = {
            'feed_id': 1,
            'headline': 'nothing in the title',
            'url': 'http://dummyurl_2.com',
            'content_id': None,
            'date': datetime.datetime(year=2018, month=1, day=1),
            'summary': 'The first mention of Queens. The second mention of Coney Island.'
        }

        results = make_article_dict(self.entry_info)

        self.assertDictEqual(results, expected)

    def test_make_tag_dict(self):

        expected = [{'article_id': 0, 'place_id': 2},
                    {'article_id': 0, 'place_id': 13}]

        results = make_tag_dict(self.entry_info, 0)

        self.assertListEqual(expected, results)

    def test_make_place_mentions_dict(self):

        expected = [{
            'tag_id': 99,
            'context': 'The first mention of Queens.',
            'location': 'summary'
        }]

        results = make_place_mentions_dict(self.entry_info, tag_id=99, place_id=2)

        self.assertListEqual(expected, results)
@unittest.skip("skipping to isolate test")
class TestExecuteInsertions(DatabaseInteractionRequired):

    def setUp(self):

        self.conn = psycopg2.connect(user=TEST_USER,
                                     dbname=TEST_DB,
                                     host=TEST_HOST)

        self.entry_info = {
            'place_tags': [2, 13],
            'place_mentions': [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 2,
                'context': 'The second mention of Queens.',
                'loc': 'title'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }],
            'articles': {
                'id': None,
                'title': 'nothing in the title',
                'link': 'http://dummyurl_2.com',
                'summary': 'The first mention of Queens. The second mention of Coney Island.',
                'date': datetime.datetime(year=2018, month=1, day=1),
                'feed_id': 1
            }
        }

    def test_execute_insertions(self):

        expected_articles = [
            (1, 1, None, 'nothing in the title', datetime.date(2018, 1, 1), 'The first mention of Queens. The second mention of Coney Island.', None, None, 'http://dummyurl_2.com')
        ]

        expected_place_tags = [
            (1, 1, 2),
            (2, 1, 13)
        ]

        expected_place_mentions = [
            (1, 1, None, 'The first mention of Queens.', 'summary'),
            (2, 1, None, 'The second mention of Queens.','title'),
            (3, 2, None, 'The second mention of Coney Island.', 'summary')
        ]

        execute_insertions(self.entry_info, self.conn)

        with self.conn.cursor() as curs:
            curs.execute("SELECT * FROM articles")
            articles = curs.fetchall()
            curs.execute("SELECT * FROM place_mentions")
            place_mentions = curs.fetchall()
            curs.execute("SELECT * FROM place_tags")
            place_tags = curs.fetchall()

        with self.subTest(msg="Insertion into articles table"):

            self.assertListEqual(expected_articles, articles)

        with self.subTest(msg="Insertion into place_tags table"):

            self.assertListEqual(expected_place_tags, place_tags)

        with self.subTest(msg="Insertion into place_mentions table"):

            self.assertListEqual(expected_place_mentions, place_mentions)


class TestDuplicateInsertion(DatabaseInteractionRequired):

    def setUp(self):

        self.conn = psycopg2.connect(user=TEST_USER,
                                     dbname=TEST_DB,
                                     host=TEST_HOST)

        self.entry_info = {
            'place_tags': [2, 13],
            'place_mentions': [
            {
                'place_id': 2,
                'context': 'The first mention of Queens.',
                'loc': 'summary'
            },
            {
                'place_id': 2,
                'context': 'The second mention of Queens.',
                'loc': 'title'
            },
            {
                'place_id': 13,
                'context': 'The second mention of Coney Island.',
                'loc': 'summary'
            }],
            'articles': {
                'id': None,
                'title': 'nothing in the title',
                'link': 'http://dummyurl_2.com',
                'summary': 'The first mention of Queens. The second mention of Coney Island.',
                'date': datetime.datetime(year=2018, month=1, day=1),
                'feed_id': 1
            }
        }

        execute_insertions(self.entry_info, self.conn)


    def test_article_insertion(self):

        execute_insertions(self.entry_info, self.conn)

        with self.conn.cursor() as curs:
            curs.execute("SELECT * FROM articles")
            results = curs.fetchall()

        self.assertEqual(len(results), 1)

    def test_place_mentions_insertion(self):

        execute_insertions(self.entry_info, self.conn)

        with self.conn.cursor() as curs:
            curs.execute("SELECT * FROM place_mentions")
            results = curs.fetchall()

        self.assertEqual(len(results), 3)

    def test_place_tags_insertion(self):

        execute_insertions(self.entry_info, self.conn)

        with self.conn.cursor() as curs:
            curs.execute("SELECT * FROM place_tags")
            results = curs.fetchall()

        self.assertEqual(len(results), 2)





if __name__ == '__main__':
    unittest.main()

