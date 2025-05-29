from fastapi import APIRouter
from .scraper import HackerNewsScraper 

router = APIRouter()
scraper = HackerNewsScraper()

@router.get("/")
async def get_front_page():
    """Get the front page articles"""
    return scraper.get_articles(1)

@router.get("/{num_pages}")
async def get_multiple_pages(num_pages: int):
    """Get articles from multiple pages"""
    return scraper.get_articles(num_pages)