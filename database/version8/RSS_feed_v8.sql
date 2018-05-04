-- database schema for RSS feeds

-- place/location tables --
CREATE TABLE media_markets(
	market_id SERIAL PRIMARY KEY,
	market_name TEXT UNIQUE NOT NULL
);

CREATE TABLE places(
  place_id SERIAL PRIMARY KEY,
	place_name TEXT NOT NULL,
	geocode VARCHAR NOT NULL,
	place_alias TEXT,
  market_id INT REFERENCES media_markets(market_id)
);

CREATE TABLE region_relations(
	place_id INT REFERENCES places(place_id),
	subplace_id INT REFERENCES places(place_id)
);

-- RSS source  --

CREATE TABLE publishers(
	pub_id SERIAL PRIMARY KEY,
	publisher TEXT NOT NULL,
	market_id INT REFERENCES media_markets(market_id));

-- RSS feed and article data --

CREATE TABLE feeds (
  feed_id SERIAL PRIMARY KEY,
	publisher_id INT REFERENCES publishers(pub_id),
	description	TEXT,
	url			TEXT NOT NULL);

  -- XML_headline_tag TEXT DEFAULT NULL,
  -- XML_subhed_tag TEXT DEFAULT NULL,
  -- XML_article_tag TEXT DEFAULT NULL,
  -- XML_permalink_tag TEXT DEFAULT NULL,
  -- scraper_article_tag TEXT DEFAULT NULL );

CREATE TABLE articles (
	article_id SERIAL PRIMARY KEY,
	feed_id INT NOT NULL REFERENCES feeds(feed_id),
	content_id TEXT UNIQUE NOT NULL,
	headline	TEXT NOT NULL,  -- title in RSS
	date	DATE NOT NULL,      -- published in RSS
	summary	TEXT,
	wordcount INT,
	page_number INT,
	url	TEXT UNIQUE NOT NULL);



CREATE TABLE place_tags(
	tag_id SERIAL PRIMARY KEY,
	article_id INT REFERENCES articles(article_id),
	place_id INT REFERENCES places(place_id),
	UNIQUE(article_id, place_id)
);


CREATE TABLE place_mentions (
  id SERIAL PRIMARY KEY,
  tag_id INT REFERENCES place_tags(tag_id),
  relevance_score SMALLINT DEFAULT NULL,
  context TEXT
);
