from fastapi import APIRouter, Depends
from .scraper import HackerNewsScraper 
from .dependencies import get_scraper

router = APIRouter()

@router.get("/")
async def get_front_page(scraper: HackerNewsScraper = Depends(get_scraper)):
    """Get the front page articles"""
    return scraper.get_articles(1)

@router.get("/cache")
async def get_cache(scraper: HackerNewsScraper = Depends(get_scraper)):
    """Get information about the current cache"""
    return scraper.get_cache_status()

@router.get("/{num_pages}")
async def get_multiple_pages(num_pages: int, scraper: HackerNewsScraper = Depends(get_scraper)):
    """Get articles from multiple pages"""
    return scraper.get_articles(num_pages)