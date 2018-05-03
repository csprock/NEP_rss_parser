-- database schema for RSS feeds

-- place/location tables --
CREATE TABLE coverage_region(
	region_id SERIAL PRIMARY KEY,
	region_name VARCHAR);

CREATE TABLE county(
	county TEXT,
	state VARCHAR(2),
	county_FIPS VARCHAR(5),
	PRIMARY KEY(county_FIPS) -- combined state code + county FIPS code
);

CREATE TABLE place(
	place TEXT,
	county_FIPS VARCHAR(5) REFERENCES county(county_FIPS),
	place_FIPS VARCHAR(5),
	PRIMARY KEY (county_FIPS, place_FIPS)  -- together these are the parts of the complete FIPS code
);


CREATE TABLE regions_to_county(
	region_id INT REFERENCES coverage_region(region_id),
	county_FIPS VARCHAR(5) REFERENCES county(county_FIPS)
);

-- RSS source  --

CREATE TABLE sources(
	source TEXT PRIMARY KEY,
	region_id INT REFERENCES coverage_region(region_id));

-- RSS feed and article data --

CREATE TABLE feeds(
	feed_id SERIAL PRIMARY KEY,
	source TEXT REFERENCES sources(source),
	feed	TEXT NOT NULL,
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
	place TEXT,
	PRIMARY KEY (article_id, place));
