import pytest
from unittest.mock import patch, Mock
from app.scraper import HackerNewsScraper
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestScraperCache:
    @pytest.fixture
    def scraper(self):
        return HackerNewsScraper()
    
    @pytest.fixture
    def mock_html_response(self):
        """Mock HTML response with a single article"""
        return """
        <tr class="athing" id="12345">
            <td><span class="titleline"><a href="https://example.com">Test Article</a></span></td>
        </tr>
        <tr>
            <td class="subtext">
                <span class="score">100 points</span> by 
                <a class="hnuser">testuser</a>
                <span class="age" title="2023-12-01T10:00:00">1 hour ago</span> | 
                <a>10 comments</a>
            </td>
        </tr>
        """
    
    @patch('app.scraper.requests.get')
    def test_cache_stores_pages(self, mock_get, scraper, mock_html_response):
        """Test that pages are stored in cache after being fetched"""
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Initial request should populate cache
        scraper.get_articles(1)
        
        # Verify cache contains page 1
        assert 1 in scraper.cache
        assert len(scraper.cache[1]) > 0
    
    @patch('app.scraper.requests.get')
    def test_cached_pages_not_fetched_again(self, mock_get, scraper, mock_html_response):
        """Test that cached pages aren't fetched again"""
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # First request - should make an HTTP request
        scraper.get_articles(1)
        assert mock_get.call_count == 1
        
        # Second request for same page - should use cache
        scraper.get_articles(1)
        # Call count should still be 1 since no new request was made
        assert mock_get.call_count == 1
    
    @patch('app.scraper.requests.get')
    def test_only_missing_pages_fetched(self, mock_get, scraper, mock_html_response):
        """Test that only missing pages are fetched"""
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # First request - page 1
        scraper.get_articles(1)
        assert mock_get.call_count == 1
        assert mock_get.call_args[0][0] == "https://news.ycombinator.com?p=1"
        
        # Second request - pages 1-3
        scraper.get_articles(3)
        # Should make 2 new requests (for pages 2 and 3)
        assert mock_get.call_count == 3
        
        # Third request - pages 1-4
        scraper.get_articles(4)
        # Should make 1 new request (for page 4)
        assert mock_get.call_count == 4
    
    @patch('app.scraper.requests.get')
    def test_cache_status_endpoint(self, mock_get, mock_html_response):
        """Test that cache status endpoint returns correct information"""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Make request to populate cache
        client.get("/2")
        
        # Check cache status
        response = client.get("/cache")
        assert response.status_code == 200
        
        cache_data = response.json()
        assert "cached_pages" in cache_data
        assert "total_articles" in cache_data
        assert "articles_per_page" in cache_data
        
        # Should have cached pages 1 and 2
        assert sorted(cache_data["cached_pages"]) == [1, 2]
    
    def test_get_cache_status(self, scraper):
        """Test that get_cache_status returns correct structure"""
        # Manually populate cache
        scraper.cache = {
            1: [{"title": "Article 1"}, {"title": "Article 2"}],
            2: [{"title": "Article 3"}]
        }
        
        cache_status = scraper.get_cache_status()
        
        assert cache_status["cached_pages"] == [1, 2]
        assert cache_status["total_articles"] == 3
        assert cache_status["articles_per_page"] == {1: 2, 2: 1}
    
    @patch('app.scraper.requests.get')
    def test_cache_doesnt_persist_after_restart(self, mock_get, mock_html_response):
        """Test that cache is empty after application restart"""
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create first scraper instance and populate cache
        first_scraper = HackerNewsScraper()
        first_scraper.get_articles(2)
        
        # Verify cache is populated
        assert len(first_scraper.cache) > 0
        assert 1 in first_scraper.cache
        assert 2 in first_scraper.cache
        
        # Create new scraper instance (simulating application restart)
        new_scraper = HackerNewsScraper()
        
        # Verify cache is empty in the new instance
        assert len(new_scraper.cache) == 0
        
        # Verify we need to make new requests after restart
        new_scraper.get_articles(1)
        assert mock_get.call_count > 0
