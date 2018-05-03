




CREATE TABLE regions(
	region_id SERIAL PRIMARY KEY,
	region_name VARCHAR NOT NULL,
	state VARCHAR(2));


CREATE TABLE places(
	place_id SERIAL PRIMARY KEY,
	place_name TEXT NOT NULL,
	region_id INT REFERENCES regions(region_id),
	other_data TEXT
);

CREATE TABLE sources(
	source_id SERIAL PRIMARY KEY,
	source_name TEXT,
	region_id INT REFERENCES regions(region_id));


CREATE TABLE feeds(
	feed_id SERIAL PRIMARY KEY,
	source_id INT REFERENCES sources(source_id),
	name	TEXT NOT NULL,
	url			TEXT NOT NULL);

CREATE TABLE article(
	id SERIAL PRIMARY KEY,
	feed_id INT REFERENCES feeds(feed_id),
	content_id	TEXT UNIQUE,
	title	TEXT NOT NULL,
	date	DATE NOT NULL,
	summary	TEXT,
	url		TEXT UNIQUE NOT NULL);


CREATE TABLE place_tags(
	article_id INT REFERENCES article(id),
	place_id INT REFERENCES places(place_id));
