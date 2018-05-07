

INSERT INTO media_markets(market_name) VALUES ('Portland');
INSERT INTO media_markets(market_name) VALUES ('San Jose');

INSERT INTO publishers(publisher, market_id) VALUES ('Portland Times', 1);
INSERT INTO publishers(publisher, market_id) VALUES ('San Jose Herald', 2);

INSERT INTO feeds(pub_id, description, url) VALUES (1, 'The Times RSS', 'dummyurl');
INSERT INTO feeds(pub_id, description, url) VALUES (2, 'SJ RSS', 'dummyurl2');

INSERT INTO places(place_name, geocode, market_id) VALUES ('Portland', 'PLDN', 1);
INSERT INTO places(place_name, geocode, market_id) VALUES ('South Portland', 'SPLDN', 1);
INSERT INTO places(place_name, geocode, market_id) VALUES ('San Jose', 'SJ', 2);
