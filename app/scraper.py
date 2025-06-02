import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from fastapi import HTTPException
from urllib.parse import urljoin
import re
from .config import BASE_URL, MAX_PAGES

class HackerNewsScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.cache = {}
    
    def scrape_page(self, page_num: int = 1) -> List[Dict]:
        """Scrape a single page of Hacker News"""

        url = f"{self.base_url}?p={page_num}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            article_rows = soup.find_all('tr', class_='athing')
            for row in article_rows:
                try:
                    article = self._extract_article_data(row)
                    if article:
                        articles.append(article)
                except Exception:
                    continue
            
            return articles
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to fetch Hacker News: {str(e)}"
            )
    
    def _extract_article_data(self, row) -> Optional[Dict]:
        """Extract article data from a row element"""
        try:
            titleline = row.find('span', class_='titleline')
            if not titleline:
                return None
                
            title_link = titleline.find('a')
            if not title_link:
                return None
                
            title = title_link.get_text(strip=True)
            url = title_link.get('href', '')
            url = urljoin(self.base_url, url)

            metadata_row = row.find_next_sibling('tr')
            
            # Initialize with defaults
            points = 0
            sent_by = "unknown"
            comments = 0
            published = None

            # Extract metadata if available
            if metadata_row:
                subtext = metadata_row.find('td', class_='subtext')
                if subtext:
                    # Extract points
                    score_span = subtext.find('span', class_='score')
                    if score_span:
                        try:
                            points_text = score_span.get_text()
                            points = re.search(r'(\d+)', points_text)
                            if points:
                                points = int(points.group(1))
                        except (ValueError, IndexError):
                            points = None
                    
                    # Extract sent_by
                    sent_by_link = subtext.find('a', class_='hnuser')
                    if sent_by_link:
                        sent_by = sent_by_link.get_text(strip=True)
                    
                    # Extract comments
                    comment_links = subtext.find_all('a')
                    for link in comment_links:
                        link_text = link.get_text(strip=True)
                        if 'comment' in link_text:
                            comment_text = link.get_text()
                            comment_match = re.search(r'(\d+)', comment_text)
                            if comment_match:
                                comments = int(comment_match.group(1))
                            break
                    
                    # Extract timestamp from age span
                    age_span = subtext.find('span', class_='age')
                    if age_span:
                        if age_span.find('a'):
                            # If the age span has a link, use its text
                            published = age_span.find('a').get_text(strip=True)
                        else:
                            published = age_span.get_text(strip=True)

            return {
                "title": title,
                "url": url,
                "points": points,
                "sent_by": sent_by,
                "published": published,
                "comments": comments
            }
            
        except Exception:
            return None
    
    def get_articles(self, num_pages: int) -> List[Dict]:
        """Get articles from multiple pages with caching"""
        if num_pages < 1 or num_pages > MAX_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Number of pages must be between 1 and {MAX_PAGES}"
            )
        
        all_articles = []
        pages_to_fetch = []
        
        # Check which pages need to be fetched
        for page in range(1, num_pages + 1):
            if page in self.cache:
                all_articles.extend(self.cache[page])
            else:
                pages_to_fetch.append(page)
        
        # Fetch only the pages not in cache
        for page in pages_to_fetch:
            articles = self.scrape_page(page)
            self.cache[page] = articles
            all_articles.extend(articles)
        
        return all_articles
    
    def get_cache_status(self) -> Dict:
        """Return information about the current cache state"""
        return {
            "cached_pages": list(self.cache.keys()),
            "total_articles": sum(len(articles) for articles in self.cache.values()),
            "articles_per_page": {page: len(articles) for page, articles in self.cache.items()}
        }