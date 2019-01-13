--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6 (Debian 10.6-1.pgdg90+1)
-- Dumped by pg_dump version 10.6 (Debian 10.6-1.pgdg90+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track execution statistics of all SQL statements executed';


SET default_with_oids = false;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.articles (
    article_id integer NOT NULL,
    feed_id integer NOT NULL,
    content_id text,
    headline text NOT NULL,
    date date NOT NULL,
    summary text,
    wordcount integer,
    page_number integer,
    url text NOT NULL
);


--
-- Name: articles_article_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.articles_article_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: articles_article_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.articles_article_id_seq OWNED BY public.articles.article_id;


--
-- Name: feeds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feeds (
    feed_id integer NOT NULL,
    pub_id integer,
    description text,
    url text
);


--
-- Name: feeds_feed_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feeds_feed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feeds_feed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feeds_feed_id_seq OWNED BY public.feeds.feed_id;


--
-- Name: keywords; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keywords (
    article_id integer NOT NULL,
    tag character varying(30) NOT NULL,
    keyword text NOT NULL
);


--
-- Name: media_markets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media_markets (
    market_id integer NOT NULL,
    market_name text NOT NULL
);


--
-- Name: media_markets_market_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.media_markets_market_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: media_markets_market_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.media_markets_market_id_seq OWNED BY public.media_markets.market_id;


--
-- Name: place_mentions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_mentions (
    id integer NOT NULL,
    tag_id integer,
    relevance_score smallint,
    context text,
    location text
);


--
-- Name: place_mentions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.place_mentions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: place_mentions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.place_mentions_id_seq OWNED BY public.place_mentions.id;


--
-- Name: place_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_tags (
    tag_id integer NOT NULL,
    article_id integer,
    place_id integer
);


--
-- Name: place_tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.place_tags_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: place_tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.place_tags_tag_id_seq OWNED BY public.place_tags.tag_id;


--
-- Name: places; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.places (
    place_id integer NOT NULL,
    place_name text NOT NULL,
    geocode character varying NOT NULL,
    place_alias text,
    market_id integer
);


--
-- Name: places_place_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.places_place_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: places_place_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.places_place_id_seq OWNED BY public.places.place_id;


--
-- Name: publishers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.publishers (
    pub_id integer NOT NULL,
    publisher text NOT NULL,
    market_id integer
);


--
-- Name: publishers_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.publishers_pub_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: publishers_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.publishers_pub_id_seq OWNED BY public.publishers.pub_id;


--
-- Name: region_relations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.region_relations (
    place_id integer,
    subplace_id integer
);


--
-- Name: articles article_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles ALTER COLUMN article_id SET DEFAULT nextval('public.articles_article_id_seq'::regclass);


--
-- Name: feeds feed_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds ALTER COLUMN feed_id SET DEFAULT nextval('public.feeds_feed_id_seq'::regclass);


--
-- Name: media_markets market_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_markets ALTER COLUMN market_id SET DEFAULT nextval('public.media_markets_market_id_seq'::regclass);


--
-- Name: place_mentions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions ALTER COLUMN id SET DEFAULT nextval('public.place_mentions_id_seq'::regclass);


--
-- Name: place_tags tag_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_tags ALTER COLUMN tag_id SET DEFAULT nextval('public.place_tags_tag_id_seq'::regclass);


--
-- Name: places place_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places ALTER COLUMN place_id SET DEFAULT nextval('public.places_place_id_seq'::regclass);


--
-- Name: publishers pub_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers ALTER COLUMN pub_id SET DEFAULT nextval('public.publishers_pub_id_seq'::regclass);


--
-- Name: articles articles_content_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_content_id_key UNIQUE (content_id);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (article_id);


--
-- Name: articles articles_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_url_key UNIQUE (url);


--
-- Name: feeds feeds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds
    ADD CONSTRAINT feeds_pkey PRIMARY KEY (feed_id);


--
-- Name: feeds feeds_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds
    ADD CONSTRAINT feeds_url_key UNIQUE (url);


--
-- Name: keywords keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (article_id, tag, keyword);


--
-- Name: media_markets media_markets_market_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_markets
    ADD CONSTRAINT media_markets_market_name_key UNIQUE (market_name);


--
-- Name: media_markets media_markets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_markets
    ADD CONSTRAINT media_markets_pkey PRIMARY KEY (market_id);


--
-- Name: place_mentions place_mentions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_pkey PRIMARY KEY (id);


--
-- Name: place_mentions place_mentions_tag_id_context_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_tag_id_context_key UNIQUE (tag_id, context);


--
-- Name: place_tags place_tags_article_id_place_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_tags
    ADD CONSTRAINT place_tags_article_id_place_id_key UNIQUE (article_id, place_id);


--
-- Name: place_tags place_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_tags
    ADD CONSTRAINT place_tags_pkey PRIMARY KEY (tag_id);


--
-- Name: places places_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_pkey PRIMARY KEY (place_id);


--
-- Name: places places_place_name_geocode_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_place_name_geocode_key UNIQUE (place_name, geocode);


--
-- Name: publishers publishers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers
    ADD CONSTRAINT publishers_pkey PRIMARY KEY (pub_id);


--
-- Name: publishers publishers_publisher_market_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers
    ADD CONSTRAINT publishers_publisher_market_id_key UNIQUE (publisher, market_id);


--
-- Name: region_relations region_relations_place_id_subplace_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.region_relations
    ADD CONSTRAINT region_relations_place_id_subplace_id_key UNIQUE (place_id, subplace_id);


--
-- Name: articles articles_feed_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_feed_id_fkey FOREIGN KEY (feed_id) REFERENCES public.feeds(feed_id);


--
-- Name: feeds feeds_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds
    ADD CONSTRAINT feeds_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.publishers(pub_id);


--
-- Name: keywords keywords_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(article_id);


--
-- Name: place_mentions place_mentions_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.place_tags(tag_id);


--
-- Name: place_tags place_tags_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_tags
    ADD CONSTRAINT place_tags_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(article_id);


--
-- Name: place_tags place_tags_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_tags
    ADD CONSTRAINT place_tags_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(place_id);


--
-- Name: places places_market_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_market_id_fkey FOREIGN KEY (market_id) REFERENCES public.media_markets(market_id);


--
-- Name: publishers publishers_market_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers
    ADD CONSTRAINT publishers_market_id_fkey FOREIGN KEY (market_id) REFERENCES public.media_markets(market_id);


--
-- Name: region_relations region_relations_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.region_relations
    ADD CONSTRAINT region_relations_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(place_id);


--
-- Name: region_relations region_relations_subplace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.region_relations
    ADD CONSTRAINT region_relations_subplace_id_fkey FOREIGN KEY (subplace_id) REFERENCES public.places(place_id);


--
-- PostgreSQL database dump complete
--

