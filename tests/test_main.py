from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_can_import_app():
    """Test that we can import the main app"""
    from app.main import app
    assert app is not None

def test_app_has_correct_title():
    """Test basic app configuration"""
    from app.main import app
    assert app.title == "Hacker News Scraper API"

class TestAPIEndpoints:
    def test_numbered_endpoint_returns_more_articles(self):
        response1 = client.get("/1")
        response2 = client.get("/2")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        articles1 = response1.json()
        articles2 = response2.json()
        
        assert len(articles2) > len(articles1), "More pages should return more articles"
    
    def test_invalid_page_numbers(self):
        response = client.get("/0")
        assert response.status_code == 400
        
        response = client.get("/-1")
        assert response.status_code == 400

class TestArticleStructure:
    def test_root_endpoint_returns_articles_with_correct_structure(self):
        response = client.get("/")
        articles = response.json()
        
        assert len(articles) > 0, "Root endpoint should return articles"
        
        required_fields = ["title", "url", "points", "comments", "author", "created_at"]
        for article in articles:
            for field in required_fields:
                assert field in article, f"Article is missing required field: {field}"
                assert article[field] is not None, f"Field {field} should not be None"
    
    def test_numbered_endpoint_returns_correct_count(self):
        """Test that /2 returns more articles than /1"""
        response1 = client.get("/1")
        response2 = client.get("/2")

        articles1 = response1.json()
        articles2 = response2.json()
        
        # This will fail with empty lists
        assert len(articles2) > len(articles1), "More pages should return more articles"
        
class TestErrorHandling:
    def test_invalid_endpoint(self):
        response = client.get("/invalid")
        assert response.status_code == 422, "Invalid endpoint should return 422"
    
    def test_invalid_method(self):
        response = client.post("/")
        assert response.status_code == 405, "POST method on root endpoint should return 405"
    
    def test_invalid_page_numbers(self):
        """Test validation for invalid page numbers"""
        response = client.get("/0")
        assert response.status_code == 400
        
        response = client.get("/-1") 
        assert response.status_code == 400
    
    def test_page_limit(self):
        """Test upper limit on page numbers"""
        response = client.get("/100")
        assert response.status_code == 400