# Hacker News Scraper API

A web scraper that fetches news articles from Hacker News with intelligent caching.

## API Endpoints

- `GET /` - Returns the front page (equivalent to `/1`)
- `GET /{number}` - Returns the specified number of pages
- `GET /cache` - Returns the pages that are currently cached in memory

### Testing the API:

The app runs on port 3000 with Docker Compose.

```sh
docker compose up -d
```

Once running, we will test it with:
```sh
curl -s localhost:3000 | jq
```

The response will be in this format:

```json
[
  {
    "title": "The title of the first news article",
    "url": "https://some-url.com/for/this/article",
    "points": 90,
    "sent_by": "pepito",
    "published": "2 hours ago",
    "comments": 24
  },
  ...
]
```

## Caching Strategy

The API implements intelligent caching:
- If `/1` is requested first, then `/2`, only page 2 is fetched
- If `/2` is requested first, then `/4`, only pages 3-4 are fetched
- Cache is in-memory and doesn't persist after restart

## Development

The project follows TDD principles:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor while keeping tests green