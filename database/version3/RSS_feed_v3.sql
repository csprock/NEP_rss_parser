-- database schema for RSS feeds

-- place/location tables --
CREATE TABLE regions(
	region_id SERIAL PRIMARY KEY,
	region_name VARCHAR,
	state VARCHAR(2));

CREATE TABLE subregions(
	subregion_id SERIAL PRIMARY KEY,
	subregion_name VARCHAR);

CREATE TABLE place_list(
	relation_id SERIAL PRIMARY KEY,
	region_id INT REFERENCES regions(region_id),
	subregion_id INT REFERENCES subregions(subregion_id));


-- RSS feed data --
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
	region_id INT REFERENCES regions(region_id),
	subregion_id INT REFERENCES subregions(subregion_id));
