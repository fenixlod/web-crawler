# web-crawler
Collecting website screenshots

## Installation:
```
cd ./bin/
chmod +x run.sh
./run.sh
```
## Use:

GET localhost:8080/isalive

POST localhost:8080/screenshots
```json
{
	"url": "https://edited.com",
	"count_links": 2
}
```
GET localhost:8080/screenshots/<screenshot_id>
	
GET localhost:8080/screenshots/<screenshot_id>/<screenshot_name>
