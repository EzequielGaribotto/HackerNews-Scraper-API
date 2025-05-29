from fastapi import FastAPI
from .scraper import HackerNewsScraper

app = FastAPI(title="Hacker News Scraper API", version="1.0.0")

# Initialize the scraper
scraper = HackerNewsScraper()

# Include the routes
from .routes import router
app.include_router(router)