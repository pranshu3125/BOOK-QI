"""
Scraper Service Module
================
Handles web scraping from multiple book data sources.
Currently supports:
- books.toscrape.com (default, for practice)
- openlibrary.org (planned)

Usage:
    from books.services.scraper import scrape_books
    books = scrape_books(source='toscrape', count=10, num_pages=2)
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)

# Registry of scraper functions
SCRAPER_REGISTRY: Dict[str, Callable] = {}


def get_chrome_driver() -> webdriver.Chrome:
    """Create and configure a headless Chrome driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def _scrape_toscrape(num_pages: int = 2) -> List[Dict]:
    """
    Scrape books from books.toscrape.com
    This is a legal practice scraping site with book catalog.
    """
    driver = None
    books_data = []
    base_url = "https://books.toscrape.com/catalogue/"
    
    rating_map = {
        'One': 1.0, 'Two': 2.0, 'Three': 3.0,
        'Four': 4.0, 'Five': 5.0
    }
    
    try:
        driver = get_chrome_driver()
        
        for page in range(1, num_pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            driver.get(url)
            time.sleep(1.5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.select('article.product_pod')
            
            if not articles:
                break
            
            for article in articles:
                try:
                    # Extract basic book info from listing
                    title_tag = article.select_one('h3 a')
                    title = title_tag.get('title', 'Unknown') if title_tag else 'Unknown'
                    
                    relative_url = title_tag.get('href', '').replace('../', '') if title_tag else ''
                    book_url = base_url + relative_url
                    
                    rating_class = article.select_one('p.star-rating')
                    rating_word = rating_class.get('class', ['One'])[1] if rating_class else 'One'
                    rating = rating_map.get(rating_word, 1.0)
                    
                    price_tag = article.select_one('p.price_color')
                    price = price_tag.get_text(strip=True) if price_tag else ''
                    
                    img_tag = article.select_one('img.thumbnail')
                    cover_url = ''
                    if img_tag:
                        src = img_tag.get('src', '')
                        cover_url = 'https://books.toscrape.com/' + src.replace('../', '')
                    
                    # Visit detail page for description and genre
                    description = ''
                    genre = 'Fiction'
                    try:
                        driver.get(book_url)
                        time.sleep(1)
                        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        
                        desc_tag = detail_soup.select_one('article.product_page p')
                        if desc_tag:
                            description = desc_tag.get_text(strip=True)
                        
                        breadcrumbs = detail_soup.select('ul.breadcrumb li')
                        if len(breadcrumbs) >= 3:
                            genre = breadcrumbs[2].get_text(strip=True)
                    except Exception as e:
                        logger.warning(f"Could not get detail for {title}: {e}")
                    
                    books_data.append({
                        'title': title,
                        'author': 'Unknown',  # This site doesn't show authors
                        'rating': rating,
                        'price': price,
                        'cover_url': cover_url,
                        'book_url': book_url,
                        'description': description[:500] if description else '',
                        'genre': genre,
                        'source': 'books.toscrape.com'
                    })
                except Exception as e:
                    logger.error(f"Error parsing book: {e}")
                    continue
        
        logger.info(f"Scraped {len(books_data)} books from books.toscrape.com")
        
    except WebDriverException as e:
        logger.error(f"WebDriver error: {e}")
    except Exception as e:
        logger.error(f"Scraping error: {e}")
    finally:
        if driver:
            driver.quit()
    
    return books_data


def _scrape_openlibrary(num_pages: int = 2) -> List[Dict]:
    """
    Placeholder for OpenLibrary scraper.
    Can be implemented similarly to toscrape scraper.
    """
    # Future implementation
    logger.info("OpenLibrary scraper not yet implemented")
    return []


def _scrape_gutenberg(num_pages: int = 2) -> List[Dict]:
    """
    Placeholder for Project Gutenberg scraper.
    """
    logger.info("Gutenberg scraper not yet implemented")
    return []


# Register available scrapers
SCRAPER_REGISTRY = {
    'toscrape': _scrape_toscrape,
    'books.toscrape.com': _scrape_toscrape,
    'openlibrary': _scrape_openlibrary,
    'gutenberg': _scrape_gutenberg,
}


def get_available_sources() -> List[str]:
    """Return list of available scraping sources."""
    return list(set(SCRAPER_REGISTRY.keys()))


def is_valid_source(source: str) -> bool:
    """Check if a source is valid."""
    return source.lower() in SCRAPER_REGISTRY


def scrape_books(
    source: str = 'toscrape',
    count: int = 10,
    num_pages: int = 2
) -> List[Dict]:
    """
    Main entry point for scraping books.
    
    Args:
        source: The scraping source. Valid options: 'toscrape', 'openlibrary', 'gutenberg'
        count: Maximum number of books to return
        num_pages: Number of pages to scrape (if source supports pagination)
    
    Returns:
        List of book dictionaries with metadata
    
    Example:
        >>> books = scrape_books(source='toscrape', count=10, num_pages=2)
        >>> len(books)
        10
    """
    # Normalize source name
    source = source.lower().strip()
    
    # Validate source
    if source not in SCRAPER_REGISTRY:
        logger.warning(f"Invalid source '{source}', defaulting to 'toscrape'")
        source = 'toscrape'
    
    # Get the appropriate scraper
    scraper_func = SCRAPER_REGISTRY.get(source, _scrape_toscrape)
    
    # Execute scraping
    books = scraper_func(num_pages=num_pages)
    
    # Limit results
    return books[:count]


def scrape_single_source(source: str, count: int = 10, num_pages: int = 2) -> Dict:
    """
    Scrape from a specific source with validation.
    
    Returns:
        Dict with 'success', 'books', 'count', 'source', 'error' keys
    """
    if not is_valid_source(source):
        return {
            'success': False,
            'books': [],
            'count': 0,
            'source': source,
            'error': f"Invalid source: {source}. Valid: {get_available_sources()}"
        }
    
    try:
        books = scrape_books(source=source, count=count, num_pages=num_pages)
        return {
            'success': True,
            'books': books,
            'count': len(books),
            'source': source,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'books': [],
            'count': 0,
            'source': source,
            'error': str(e)
        }