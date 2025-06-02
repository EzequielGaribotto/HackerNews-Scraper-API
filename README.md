# Hacker News Scraper API

A web scraper that fetches news articles from Hacker News with intelligent caching.

## API Endpoints

- `GET /` - Returns the front page (equivalent to `/1`)
- `GET /{number}` - Returns the specified number of pages
- `GET /cache` - Returns the pages that are currently cached in memory

### Running the API:

The app runs on port 3000 with Docker Compose.

First time setup or after changing requirements/Dockerfile
```sh
docker compose up -d --build
```

For routine startup, you can use:
```sh
docker compose up -d
```

## Caching Strategy

The API implements intelligent caching:
- If `/1` is requested first, then `/2`, only page 2 is fetched
- If `/2` is requested first, then `/4`, only pages 3-4 are fetched
- Cache is in-memory and doesn't persist after restart

### Restart API:

```sh
docker compose restart hackernews-api
```

### Run tests

Run the validation tests with:
```sh
docker compose exec hackernews-api pytest ./tests -v
```

### Usage example

Fetch the first three pages of articles:
```sh
curl -s localhost:3000/3 | jq
```

This will return the articles from the first three pages in this format:

```json
[
  {
    "title": "The title of the first news article on page 1",
    "url": "https://some-url.com/for/this/article",
    "points": 90,
    "sent_by": "pepito",
    "published": "2 hours ago",
    "comments": 24
  },
  ...
]
```

To see the cached pages and their articles, you can use:
```sh
curl -s localhost:3000/cache | jq
```

Will return the cached pages in this format:

```json
{
  "cached_pages": [1, 2, 3],
  "total_articles": 90,
  "articles_per_page": {
    "1": 30,
    "2": 30,
    "3": 30
  }
}
```



## Development

The project follows TDD principles:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor, update and fix functionalities while keeping tests green