import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.main import HackerNewsScraper

class TestHackerNewsScraper:
    
    @pytest.fixture
    def scraper(self):
        return HackerNewsScraper()
    
    @pytest.fixture
    def mock_html_response(self):
        """Mock HTML response from Hacker News"""
        return """
        <html>
        <tr class="athing" id="12345">
            <td>
                <span class="titleline">
                    <a href="https://example.com">Test Article Title</a>
                </span>
            </td>
        </tr>
        <tr>
            <td class="subtext">
                <span class="score">150 points</span> by 
                <a class="hnuser" href="user?id=testuser">testuser</a>
                <span class="age" title="2023-12-01T10:00:00">2 hours ago</span> | 
                <a href="item?id=12345">25 comments</a>
            </td>
        </tr>
        </html>
        """
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_success(self, mock_get, scraper, mock_html_response):
        """Test successful page scraping"""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None # Simulate successful request
        mock_get.return_value = mock_response
        
        # Execute
        articles = scraper.scrape_page(1)
        
        # Assert
        assert len(articles) == 1
        article = articles[0]
        assert article["title"] == "Test Article Title"
        assert article["url"] == "https://example.com"
        assert article["points"] == 150
        assert article["author"] == "testuser"
        assert article["comments"] == 25
        assert "created_at" in article
        
        # Verify request was made correctly
        mock_get.assert_called_once_with("https://news.ycombinator.com?p=1")
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_with_page_number(self, mock_get, scraper, mock_html_response):
        """Test scraping with specific page number"""
        mock_response = Mock()
        mock_response.content = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        scraper.scrape_page(2)
        
        mock_get.assert_called_once_with("https://news.ycombinator.com?p=2")
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_handles_relative_urls(self, mock_get, scraper):
        """Test handling of relative URLs"""
        html_with_relative_url = """
        <tr class="athing" id="12345">
            <td>
                <span class="titleline">
                    <a href="item?id=12345">Discussion Article</a>
                </span>
            </td>
        </tr>
        <tr>
            <td class="subtext">
                <span class="score">50 points</span> by 
                <a class="hnuser" href="user?id=testuser">testuser</a>
                <span class="age" title="2023-12-01T10:00:00">1 hour ago</span> | 
                <a href="item?id=12345">10 comments</a>
            </td>
        </tr>
        """
        
        mock_response = Mock()
        mock_response.content = html_with_relative_url
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = scraper.scrape_page(1)
        
        assert articles[0]["url"] == "https://news.ycombinator.com/item?id=12345"
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_handles_missing_metadata_field(self, mock_get, scraper):
        """Test handling of articles with missing fields"""
        html_missing_fields = """
        <tr class="athing" id="12345">
            <td>
                <span class="titleline">
                    <a href="https://example.com">Title Only Article</a>
                </span>
            </td>
        </tr>
        <tr>
            <td class="subtext">
            </td>
        </tr>
        """
        
        mock_response = Mock()
        mock_response.content = html_missing_fields
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = scraper.scrape_page(1)
        
        assert len(articles) == 1
        article = articles[0]
        assert article["title"] == "Title Only Article"
        assert article["url"] == "https://example.com"
        assert "created_at" in article
        assert article["points"] == 0
        assert article["author"] == "unknown"
        assert article["comments"] == 0
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_network_error(self, mock_get, scraper):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(HTTPException) as exc_info:
            scraper.scrape_page(1)
        
        assert exc_info.value.status_code == 500
        assert "Failed to fetch Hacker News" in str(exc_info.value.detail)
    
    @patch('app.scraper.requests.get')
    def test_scrape_page_malformed_html(self, mock_get, scraper):
        """Test handling of malformed HTML"""
        mock_response = Mock()
        mock_response.content = "<html><body>No valid articles</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = scraper.scrape_page(1)
        
        assert articles == []
    
    def test_get_articles_invalid_pages(self, scraper):
        """Test validation of page numbers"""
        with pytest.raises(HTTPException) as exc_info:
            scraper.get_articles(0)
        assert exc_info.value.status_code == 400
        
        with pytest.raises(HTTPException) as exc_info:
            scraper.get_articles(-1)
        assert exc_info.value.status_code == 400
        
        with pytest.raises(HTTPException) as exc_info:
            scraper.get_articles(11)
        assert exc_info.value.status_code == 400