-- database schema for RSS feeds

-- places section --

CREATE TABLE place_names(
	place_id SERIAL,
	place_name VARCHAR,
	PRIMARY KEY(place_id, place_name));

CREATE TABLE regions(
	region_id SERIAL PRIMARY KEY,
	place_id INT,
	region_name VARCHAR,
	FOREIGN KEY(place_id, region_name) REFERENCES place_names(place_id, place_name));

CREATE TABLE subregions(
	subregion_id SERIAL PRIMARY KEY,
	place_id INT,
	subregion_name VARCHAR,
	FOREIGN KEY(place_id, subregion_name) REFERENCES place_names(place_id, place_name));

CREATE TABLE relations(
	rel_id SERIAL PRIMARY KEY,
	region_id INT REFERENCES regions(region_id),
	subregion_id INT REFERENCES subregions(subregion_id));


-- article section --

CREATE TABLE sources(
	source TEXT PRIMARY KEY,
	region INT REFERENCES regions(region_id));


CREATE TABLE feeds(
	id SERIAL PRIMARY KEY,
	source TEXT REFERENCES sources(source),
	name	TEXT NOT NULL,
	url			TEXT NOT NULL);

CREATE TABLE article(
	id SERIAL PRIMARY KEY,
	feed_id INT REFERENCES feeds(id),
	content_id	TEXT UNIQUE,
	title	TEXT NOT NULL,
	date	DATE NOT NULL,
	summary	TEXT,
	url		TEXT UNIQUE NOT NULL);


CREATE TABLE place_tags(
	article_id INT REFERENCES article(id),
	place_id INT,
	place_name VARCHAR,
	FOREIGN KEY(place_id, place_name) REFERENCES place_names(place_id, place_name));
