-- reset the content part of the rss database

DELETE FROM place_tags WHERE article_id > 0;
DELETE FROM article WHERE id > 0;
ALTER SEQUENCE article_id_seq WITH RESTART;
 