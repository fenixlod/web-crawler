#!/usr/bin/python3

"""
Simple http server with following endpoints:
GET /isalive
	Response:
	{ 
		"status": "running"
	}

POST /screenshots
	Request:
	{
		"url": "https://edited.com",
		"count_links": 2
	}
	Response:
	{
		"screenshot_id": 1
	}
	
GET /screenshots/<screenshot_id:int>
	Response:
	[
		{
			"screenshot_index": 1,
			"screenshot_url": "https://edited.com",
			"count_links": 3,
			"screenshots": [
				1.png, 2.png, 3.png, 4.png
			]
		}
	]
	
GET /screenshots/<screenshot_id:int>/<name>
	Response:
	png image
"""

import bottle, json, logging, os, time, psycopg2, database as db, webcrawler, asyncio
from bottle import run, get, post, request, response, static_file
from logging.handlers import RotatingFileHandler
from pydantic import BaseModel, field_validator
from threading import Thread

screenshots_dir = '/app/screenshots'

class ScreenshotRequest(BaseModel):
	url: str
	count_links: int

	@field_validator('url')
	def validate_url(cls, value: str) -> str:
		if not value:
			raise ValueError("Url must not be empty")
		return value
		
	@field_validator('count_links')
	def validate_count_links(cls, value: int) -> int:
		if value < 1 or value > 100:
			raise ValueError("Count links must be between 1 and 100")
		return value

#--------------------------------------------------------
# Brief: Eddpoint used for tracking server health
#--------------------------------------------------------
@get('/isalive')
def is_alive():
	logger.info('GET /isalive')
	response_body = { 'status': 'running' }
	return response_body

#--------------------------------------------------------
# Brief: Endpoint for starting the process of web page crawling and shooting of the web pages.
# Expects JSON body, with 2 parameters 'url' and 'count_links'.
#--------------------------------------------------------
@post('/screenshots')
def create_screenshots():
	try:
		screenshots = ScreenshotRequest.model_validate_json(json.dumps(request.json))
		logger.info(f'POST /screenshots: {screenshots}')
		operation_id = db.insert_screenshot(screenshots.url, screenshots.count_links)
		logger.info(f'Operation_id: {operation_id}')
		Thread(target=webcrawler.synced_archive_web_page, args=(screenshots.url, screenshots.count_links, operation_id)).start()
		logger.info('Screenshoting started:')
		response.status = 202
		return { 'screenshot_id': operation_id }
	except Exception as ex:
		logger.exception('Error while creating screenshot request')
		response.status = 400
		return { 'error': f'{str(ex)}' }

#--------------------------------------------------------
# Brief: Endpoint used to return collected screenshots for the provided id
#--------------------------------------------------------
@get('/screenshots/<id:int>')
def get_screenshots(id: int):
	try:
		logger.info(f'GET /screenshots: {id}')
		screenshot = db.get_screenshot(id)
		if not len(screenshot):
			response.status = 404
			return { 'error': 'Not found' }
		
		base_dir = os.path.join(screenshots_dir, str(id))
		return { 
			'screenshot_index': screenshot[0][0],
			'screenshot_url': screenshot[0][1],
			'count_links': screenshot[0][2],
			'screenshots': list([f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))])
		}
	except Exception as ex:
		logger.exception('Error while fetching screenshots')
		response.status = 500
		return { 'error': f'{str(ex)}' }

#--------------------------------------------------------
# Brief: Endpoint used to return collected screenshot for the provided id and file name
#--------------------------------------------------------
@get('/screenshots/<id:int>/<name>')
def get_screenshot(id: int, name: str):
	try:
		logger.info(f'GET /screenshot/{id}/{name}')
		base_dir = os.path.join(screenshots_dir, str(id))
		return static_file(name, root=base_dir, mimetype='image/png')
	except Exception as ex:
		logger.exception('Error while fetching screenshots')
		response.status = 500
		return { 'error': f'{str(ex)}' }

#--------------------------------------------------------
# Brief: Initialize the logging.
#--------------------------------------------------------
def init_logging():
	logger = logging.getLogger('web_server_logger')
	logger.propagate = False
	logger_handler = RotatingFileHandler(filename='/app/logs/web-server.log', maxBytes=10 * 1024 * 1024, backupCount=10)
	logger_handler.setFormatter(logging.Formatter('[%(asctime)s] - %(message)s'))
	logger.addHandler(logger_handler)
	logger.addHandler(logging.StreamHandler())
	logger.setLevel(level=logging.INFO)
	return logger

if __name__ == "__main__":
	logger = init_logging()
	time.sleep(5) #This is ugly. Waiting for postgre container to start
	db_version = db.query_db('SELECT version()')
	logger.info(f'PostgreSQL database version: {db_version}')
	db_init_result = db.init()
	logger.info(f'Database init: {db_init_result}')
	run(host='0.0.0.0', port=8080)

