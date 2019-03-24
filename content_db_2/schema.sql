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


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.articles (
    id integer NOT NULL,
    feed_id integer NOT NULL,
    headline text NOT NULL,
    date date NOT NULL,
    summary text,
    byline character varying(255),
    wordcount integer,
    page_number integer,
    url text NOT NULL
);


--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.articles_id_seq OWNED BY public.articles.id;


--
-- Name: feeds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feeds (
    id integer NOT NULL,
    publisher_id integer,
    description text NOT NULL,
    url text NOT NULL,
    xml_headline_tag text,
    xml_subhed_tag text,
    xml_article_tag text,
    xml_permalink_tag text,
    scraper_article_tag text
);


--
-- Name: feeds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feeds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feeds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feeds_id_seq OWNED BY public.feeds.id;


--
-- Name: keywords; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keywords (
    article_id integer NOT NULL,
    tag character varying(30),
    keyword text
);


--
-- Name: media_markets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media_markets (
    id integer NOT NULL,
    market_name text
);


--
-- Name: media_markets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.media_markets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: media_markets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.media_markets_id_seq OWNED BY public.media_markets.id;


--
-- Name: place_aliases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_aliases (
    place_id integer NOT NULL,
    place_name text,
    not_followed_by text,
    not_preceded_by text
);


--
-- Name: place_geocodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_geocodes (
    place_id integer NOT NULL,
    geocode character varying,
    population integer,
    poverty_rate numeric,
    pct_white numeric
);


--
-- Name: places; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.places (
    id integer NOT NULL,
    market_id integer
);


--
-- Name: ny_geocodes; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.ny_geocodes AS
 SELECT place_aliases.place_name,
    place_geocodes.geocode
   FROM (((public.media_markets
     JOIN public.places ON ((places.market_id = media_markets.id)))
     JOIN public.place_aliases ON ((places.id = place_aliases.place_id)))
     JOIN public.place_geocodes ON ((places.id = place_geocodes.place_id)))
  WHERE (places.market_id = 2);


--
-- Name: place_demographics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_demographics (
    place_id integer,
    population integer,
    poverty_rate real,
    pct_white real
);


--
-- Name: place_mentions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.place_mentions (
    id integer NOT NULL,
    article_id integer NOT NULL,
    relevance_score smallint,
    context text,
    place_id integer
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
-- Name: places_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.places_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: places_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.places_id_seq OWNED BY public.places.id;


--
-- Name: publishers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.publishers (
    id integer NOT NULL,
    publisher text,
    market_id integer
);


--
-- Name: publishers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.publishers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: publishers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.publishers_id_seq OWNED BY public.publishers.id;


--
-- Name: region_relations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.region_relations (
    subregion_id integer NOT NULL,
    parent_region_id integer NOT NULL
);


--
-- Name: articles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles ALTER COLUMN id SET DEFAULT nextval('public.articles_id_seq'::regclass);


--
-- Name: feeds id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds ALTER COLUMN id SET DEFAULT nextval('public.feeds_id_seq'::regclass);


--
-- Name: media_markets id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_markets ALTER COLUMN id SET DEFAULT nextval('public.media_markets_id_seq'::regclass);


--
-- Name: place_mentions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions ALTER COLUMN id SET DEFAULT nextval('public.place_mentions_id_seq'::regclass);


--
-- Name: places id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places ALTER COLUMN id SET DEFAULT nextval('public.places_id_seq'::regclass);


--
-- Name: publishers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers ALTER COLUMN id SET DEFAULT nextval('public.publishers_id_seq'::regclass);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- Name: articles articles_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_url_key UNIQUE (url);


--
-- Name: feeds feeds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds
    ADD CONSTRAINT feeds_pkey PRIMARY KEY (id);


--
-- Name: keywords keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (article_id);


--
-- Name: media_markets media_markets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_markets
    ADD CONSTRAINT media_markets_pkey PRIMARY KEY (id);


--
-- Name: place_mentions place_mentions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_pkey PRIMARY KEY (id);


--
-- Name: places places_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_pkey PRIMARY KEY (id);


--
-- Name: publishers publishers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers
    ADD CONSTRAINT publishers_pkey PRIMARY KEY (id);


--
-- Name: articles articles_feed_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_feed_id_fkey FOREIGN KEY (feed_id) REFERENCES public.feeds(id);


--
-- Name: feeds feeds_publisher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feeds
    ADD CONSTRAINT feeds_publisher_id_fkey FOREIGN KEY (publisher_id) REFERENCES public.publishers(id);


--
-- Name: keywords keywords_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);


--
-- Name: place_demographics place_demographics_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_demographics
    ADD CONSTRAINT place_demographics_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id);


--
-- Name: place_mentions place_mentions_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);


--
-- Name: place_mentions place_mentions_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.place_mentions
    ADD CONSTRAINT place_mentions_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id);


--
-- Name: places places_market_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_market_id_fkey FOREIGN KEY (market_id) REFERENCES public.media_markets(id);


--
-- Name: publishers publishers_market_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.publishers
    ADD CONSTRAINT publishers_market_id_fkey FOREIGN KEY (market_id) REFERENCES public.media_markets(id);


--
-- Name: region_relations region_relations_parent_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.region_relations
    ADD CONSTRAINT region_relations_parent_region_id_fkey FOREIGN KEY (parent_region_id) REFERENCES public.places(id);


--
-- Name: region_relations region_relations_subregion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.region_relations
    ADD CONSTRAINT region_relations_subregion_id_fkey FOREIGN KEY (subregion_id) REFERENCES public.places(id);


--
-- PostgreSQL database dump complete
--

