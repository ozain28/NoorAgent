import urllib.parse
from playwright.sync_api import sync_playwright

def search_web(query: str) -> str:
    """Playwright ka istemal karke Google search perform karta hai"""
    try:
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        with sync_playwright() as p:
            # Custom user-agent to prevent bot detection
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Go to search URL and wait for headings to load
            page.goto(search_url, timeout=10000)
            page.wait_for_selector("h3", timeout=5000)
            
            # Extract search titles
            titles = page.locator("h3").all_inner_texts()
            browser.close()
            
            # Filter out empty strings
            valid_results = [title.strip() for title in titles if title.strip()]
            
            if valid_results:
                return f"Search Results for '{query}':\n" + "\n".join(f"- {t}" for t in valid_results[:5])
            else:
                return f"'{query}' ke liye koi search results nahi mile."
                
    except Exception as e:
        return f"Browser Search Error: {str(e)}"