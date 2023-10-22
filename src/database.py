#!/usr/bin/python3

import psycopg2, os
from dotenv import load_dotenv

load_dotenv()

create_screenshots_table='''
CREATE SEQUENCE IF NOT EXISTS public.screenshots_id_seq
	INCREMENT 1
	START 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	CACHE 1;

ALTER SEQUENCE public.screenshots_id_seq
	OWNER TO postgres;
	
CREATE TABLE IF NOT EXISTS public.screenshots
(
	id bigint NOT NULL DEFAULT nextval('screenshots_id_seq'::regclass),
	url character varying(255) COLLATE pg_catalog."default" NOT NULL,
	count_links integer NOT NULL,
	CONSTRAINT screenshots_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.screenshots
	OWNER to postgres;
	
ALTER SEQUENCE screenshots_id_seq
OWNED BY screenshots.id;
'''

insert_screenshot_template='''
INSERT INTO screenshots (url, count_links) VALUES (%s, %s);
SELECT currval('screenshots_id_seq');
'''

get_screenshot_template='''
SELECT * 
FROM screenshots
WHERE id = %s;
'''

#--------------------------------------------------------
# Brief: Open new connection to the database
#--------------------------------------------------------
def get_db_connection():
	conn = psycopg2.connect(
		host=os.environ.get('DATABASE_URL'),
		port=os.environ.get('DATABASE_PORT'),
		database=os.environ.get('DATABASE_NAME'),
		user=os.environ.get('DATABASE_USER_NAME'),
		password=os.environ.get('DATABASE_USER_PASSWORD')
	)
	return conn

#--------------------------------------------------------
# Brief: Initialize the database. Create all tables if not exist.
#--------------------------------------------------------
def init():
	return query_db(create_screenshots_table)
	
#--------------------------------------------------------
# Brief: Execute database query and returns all results. NOTE: not good implementation,
# if too many results are returned it is posible to go Out of Memoty.
#--------------------------------------------------------
def query_db(query: str, *args):
	retult = None
	with get_db_connection() as connection:
		with connection.cursor() as cur:
			cur.execute(query, (args))
			result = [] if cur.rowcount < 1 else cur.fetchall()
			print(result)
		connection.commit() 
	return result

#--------------------------------------------------------
# Brief: Insert new screenshot into db. Returns the id of the created screenshot.
#--------------------------------------------------------
def insert_screenshot(url: str, count_links: int) -> int:
	return query_db(insert_screenshot_template, url, count_links)[0][0]

#--------------------------------------------------------
# Brief: Get screenshot info.
#--------------------------------------------------------
def get_screenshot(screenshot_id: int):
	return query_db(get_screenshot_template, screenshot_id)

if __name__ == "__main__":
	db_version = query_db('SELECT version()')
	print(f'PostgreSQL database version: {db_version}')

