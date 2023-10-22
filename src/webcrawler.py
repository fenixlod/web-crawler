#!/usr/bin/python

import asyncio, os, requests, logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logger = logging.getLogger('web_server_logger')
screenshots_dir = '/app/screenshots'

#--------------------------------------------------------
# Brief: Finds the first N links in web page. 
#--------------------------------------------------------
def collect_urls_from_web_page(url: str, count_urls: int) -> set[str]:
	urls_to_screenshot = set()
	urls_to_screenshot.add(url)
	try:
		response = requests.get(url, headers={'accept': 'text/html', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0'})
		response.raise_for_status()
		soup = BeautifulSoup(response.text, 'html.parser')
		
		if count_urls:
			for link in soup.find_all('a'):
				href = link.get('href')
				if href.startswith('http'):
					urls_to_screenshot.add(href)
					
				if len(urls_to_screenshot) >= count_urls + 1:
					break
		
	except Exception as ex:
		logger.exception('Error while collecting urls from web page')
		
	return urls_to_screenshot

#--------------------------------------------------------
# Brief: Takes screenshots of url. 
#--------------------------------------------------------
async def screenshot_url(url: str, operation_id: int, index: int) -> None:
	try:
		async with async_playwright() as p:
			browser = await p.chromium.launch()
			page = await browser.new_page()
			await page.goto(url)
			await page.screenshot(path=f'{screenshots_dir}/{operation_id}/{index}.png')
			await browser.close()
	except Exception as ex:
		logger.exception('Error while creating screenshot')

#--------------------------------------------------------
# Brief: Finds the first N links in web page and takes screenshots of the initial page and the found links. 
#--------------------------------------------------------
async def archive_web_page(url: str, count_links: int, operation_id: int) -> None:
	links = collect_urls_from_web_page(url, count_links)
	tasks = []
	for idx, link in enumerate(links):
		logger.info(f'Starting screenshot of url: {link}')
		task = asyncio.create_task(screenshot_url(link, operation_id, idx + 1))
		tasks.append(task)
	
	for task in tasks:
		await task
	
	logger.info(f'All screenshots of web page: {url} done.')
	
def synced_archive_web_page(url: str, count_links: int, operation_id: int) -> None:
	asyncio.run(archive_web_page(url, count_links, operation_id))

if __name__ == "__main__":
	print('Start main')
	asyncio.run(archive_web_page('https://edited.com', 2, 4))
	print('End main')

