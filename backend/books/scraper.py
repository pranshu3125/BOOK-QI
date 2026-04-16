from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import random

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def parse_goodreads_book(url):
    driver = get_driver()
    books_data = []
    
    try:
        driver.get(url)
        time.sleep(3)
        
        for i in range(3):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            book_cards = soup.select('div[data-testid="bookListBookCover"]')
            
            if not book_cards:
                book_cards = soup.select('.bookListItem')
            
            if not book_cards:
                book_cards = soup.select('[class*="BookCard"]')
            
            for card in book_cards[:10]:
                try:
                    title_elem = card.select_one('[data-testid="bookTitle"]')
                    if not title_elem:
                        title_elem = card.select_one('a[class*="title"]')
                    title = title_elem.text.strip() if title_elem else "Unknown Title"
                    
                    author_elem = card.select_one('[data-testid="bookMetaAuthorLink"]')
                    if not author_elem:
                        author_elem = card.select_one('a[class*="author"]')
                    author = author_elem.text.strip() if author_elem else "Unknown Author"
                    
                    rating = None
                    rating_elem = card.select_one('[data-testid="bookAvgRating"]')
                    if rating_elem:
                        rating_text = rating_elem.text.strip()
                        try:
                            rating = float(rating_text.split()[0])
                        except:
                            pass
                    
                    cover_url = ""
                    cover_elem = card.select_one('img')
                    if cover_elem:
                        cover_url = cover_elem.get('src', '')
                    
                    description = ""
                    desc_elem = card.select_one('[data-testid="bookDescription"]')
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    book_url = ""
                    link_elem = card.select_one('a[class*="title"]')
                    if link_elem:
                        book_url = link_elem.get('href', '')
                        if book_url and not book_url.startswith('http'):
                            book_url = f"https://www.goodreads.com{book_url}"
                    
                    books_data.append({
                        'title': title,
                        'author': author,
                        'rating': rating,
                        'cover_url': cover_url,
                        'description': description,
                        'book_url': book_url,
                        'genre': 'Fiction'
                    })
                    
                except Exception as e:
                    continue
            
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="paginationNextButton"]')
                if next_button:
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
            except:
                break
                
    except Exception as e:
        print(f"Error parsing Goodreads: {e}")
    finally:
        driver.quit()
    
    return books_data

def parse_openlibrary_book(url):
    driver = get_driver()
    books_data = []
    
    try:
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        book_cards = soup.select('div.bookcover')
        
        if not book_cards:
            book_cards = soup.select('[class*="book"]')
        
        for card in book_cards[:10]:
            try:
                title_elem = card.select_one('a.title')
                title = title_elem.text.strip() if title_elem else "Unknown Title"
                
                author = "Unknown Author"
                author_elem = card.select_one('a.author')
                if author_elem:
                    author = author_elem.text.strip()
                
                cover_url = ""
                cover_elem = card.select_one('img')
                if cover_elem:
                    cover_url = cover_elem.get('src', '')
                
                book_url = ""
                if title_elem:
                    book_url = title_elem.get('href', '')
                    if book_url and not book_url.startswith('http'):
                        book_url = f"https://openlibrary.org{book_url}"
                
                books_data.append({
                    'title': title,
                    'author': author,
                    'rating': None,
                    'cover_url': cover_url,
                    'description': '',
                    'book_url': book_url,
                    'genre': 'Fiction'
                })
                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error parsing OpenLibrary: {e}")
    finally:
        driver.quit()
    
    return books_data

def scrape_books(sources=['goodreads'], count=10):
    all_books = []
    
    if 'goodreads' in sources:
        goodreads_books = parse_goodreads_book("https://www.goodreads.com/list/show/1.Best_Books_Ever")
        all_books.extend(goodreads_books)
    
    if 'openlibrary' in sources:
        ol_books = parse_openlibrary_book("https://openlibrary.org/subjects/fiction")
        all_books.extend(ol_books)
    
    return all_books[:count]
