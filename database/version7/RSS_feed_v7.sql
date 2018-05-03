-- database schema for RSS feeds

-- place/location tables --
CREATE TABLE media_markets(
	id SERIAL PRIMARY KEY,
	market_name TEXT
);

CREATE TABLE places(
  id SERIAL PRIMARY KEY,
	place_name TEXT,
	place_aliases TEXT,
	geocode VARCHAR,
  not_followed_by TEXT,
  not_preceded_by TEXT,
  market_id INT REFERENCES media_markets(id)
);

CREATE TABLE region_relations(
	subregion_id INT NOT NULL REFERENCES places(id),
	parent_region_id INT NOT NULL REFERENCES places(id)
);

-- RSS source  --

CREATE TABLE publishers(
	id SERIAL PRIMARY KEY,
	publisher TEXT,
	market_id INT REFERENCES media_markets(id));

-- RSS feed and article data --

CREATE TABLE feeds (
  id SERIAL PRIMARY KEY,
	publisher_id INT REFERENCES publishers(id),
	description	TEXT NOT NULL,
	url			TEXT NOT NULL,
  XML_headline_tag TEXT DEFAULT NULL,
  XML_subhed_tag TEXT DEFAULT NULL,
  XML_article_tag TEXT DEFAULT NULL,
  XML_permalink_tag TEXT DEFAULT NULL,
  scraper_article_tag TEXT DEFAULT NULL );

CREATE TABLE articles (
	id SERIAL PRIMARY KEY,
	feed_id INT NOT NULL REFERENCES feeds(id),
	headline	TEXT NOT NULL,
	date	DATE NOT NULL,
	summary	TEXT,
	byline VARCHAR(255),
	wordcount INT,
	page_number INT,
	url	TEXT UNIQUE NOT NULL);

CREATE TABLE place_tags(
	id SERIAL PRIMARY KEY,
	article_id INT REFERENCES articles(id),
	place_id INT REFERENCES places(id),
	UNIQUE(article_id, place_id)
);


CREATE TABLE place_mentions (
  id SERIAL PRIMARY KEY,
  tag_id INT REFERENCES place_tags(id),
  relevance_score SMALLINT DEFAULT NULL,
  context TEXT
);
