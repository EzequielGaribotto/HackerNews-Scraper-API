from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from fastapi import HTTPException
import requests
from urllib.parse import urljoin

class HackerNewsScraper:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com"
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
            author = "unknown"
            comments = 0
            created_at = None

            # Extract metadata if available
            if metadata_row:
                subtext = metadata_row.find('td', class_='subtext')
                if subtext:
                    # Extract points
                    score_span = subtext.find('span', class_='score')
                    if score_span:
                        try:
                            points_text = score_span.get_text(strip=True)
                            points = int(points_text.split()[0])
                        except (ValueError, IndexError):
                            points = None
                    
                    # Extract author
                    author_link = subtext.find('a', class_='hnuser')
                    if author_link:
                        author = author_link.get_text(strip=True)
                    
                    # Extract comments
                    comment_links = subtext.find_all('a')
                    for link in comment_links:
                        link_text = link.get_text(strip=True)
                        if 'comment' in link_text:
                            try:
                                comments = int(link_text.split()[0])
                            except (ValueError, IndexError):
                                comments = None
                            break
                    
                    # Extract timestamp from age span
                    age_span = subtext.find('span', class_='age')
                    if age_span and age_span.get('title'):
                        created_at = age_span.get('title')
            
            return {
                "title": title,
                "url": url,
                "points": points,
                "author": author,
                "comments": comments,
                "created_at": created_at
            }
            
        except Exception:
            return None
    
    def get_articles(self, num_pages: int) -> List[Dict]:
        """Get articles from multiple pages with caching"""
        if num_pages < 1 or num_pages > 10:
            raise HTTPException(
                status_code=400, 
                detail="Number of pages must be between 1 and 10"
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