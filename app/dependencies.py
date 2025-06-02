from .scraper import HackerNewsScraper

# Singleton instance
_scraper = None

def get_scraper():
    global _scraper
    if _scraper is None:
        _scraper = HackerNewsScraper()
    return _scraper

def reset_scraper():
    """Reset the scraper instance, useful for testing or reinitialization."""
    global _scraper
    _scraper = None