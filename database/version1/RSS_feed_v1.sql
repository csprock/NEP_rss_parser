-- database schema for RSS feeds

CREATE TABLE sources(
	source TEXT PRIMARY KEY,
	location TEXT);


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
	place VARCHAR(150) NOT NULL,
	PRIMARY KEY(article_id, place));

-- filter table of places
CREATE TABLE filters(
	source TEXT REFERENCES sources(source) PRIMARY KEY,
	filters JSONB);
