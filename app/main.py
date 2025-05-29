from fastapi import FastAPI

app = FastAPI(title="Hacker News Scraper API", version="1.0.0")

@app.get("/")
async def get_front_page():
    return []

@app.get("/{num_pages}")
async def get_multiple_pages(num_pages: int):
    return []