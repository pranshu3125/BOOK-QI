from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time

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

def scrape_books_toscrape(num_pages=2):
    """Scrape books.toscrape.com - a legal practice scraping site."""
    driver = get_driver()
    books_data = []
    base_url = "https://books.toscrape.com/catalogue/"
    
    rating_map = {'One': 1.0, 'Two': 2.0, 'Three': 3.0, 'Four': 4.0, 'Five': 5.0}
    
    try:
        page = 1
        while page <= num_pages:
            url = "https://books.toscrape.com/catalogue/page-{}.html".format(page)
            driver.get(url)
            time.sleep(1.5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            articles = soup.select('article.product_pod')
            if not articles:
                break
                
            for article in articles:
                try:
                    title_tag = article.select_one('h3 a')
                    title = title_tag['title'] if title_tag else 'Unknown'
                    
                    relative_url = title_tag['href'].replace('../', '') if title_tag else ''
                    book_url = base_url + relative_url
                    
                    rating_class = article.select_one('p.star-rating')
                    rating_word = rating_class['class'][1] if rating_class else 'One'
                    rating = rating_map.get(rating_word, 1.0)
                    
                    price_tag = article.select_one('p.price_color')
                    price = price_tag.text.strip() if price_tag else ''
                    
                    img_tag = article.select_one('img.thumbnail')
                    cover_url = 'https://books.toscrape.com/' + img_tag['src'].replace('../', '') if img_tag else ''
                    
                    description = ''
                    genre = 'Fiction'
                    try:
                        driver.get(book_url)
                        time.sleep(1)
                        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        desc_tag = detail_soup.select_one('article.product_page p')
                        if desc_tag:
                            description = desc_tag.text.strip()
                        breadcrumbs = detail_soup.select('ul.breadcrumb li')
                        if len(breadcrumbs) >= 3:
                            genre = breadcrumbs[2].text.strip()
                    except:
                        pass
                    
                    books_data.append({
                        'title': title,
                        'author': 'Unknown',
                        'rating': rating,
                        'price': price,
                        'cover_url': cover_url,
                        'book_url': book_url,
                        'description': description,
                        'genre': genre,
                    })
                except Exception as e:
                    print(f"Error parsing book: {e}")
                    continue
            
            page += 1
            
    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        driver.quit()
    
    return books_data

def scrape_books(sources=None, count=10, num_pages=2):
    """Main entry point. Scrapes books.toscrape.com by default."""
    books = scrape_books_toscrape(num_pages=num_pages)
    return books[:count]