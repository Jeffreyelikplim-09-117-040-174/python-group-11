import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
from app.core.config import settings

class CompetitorPriceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def scrape_amazon_price(self, product_url: str) -> Optional[float]:
        """Scrape price from Amazon"""
        try:
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different price selectors
            price_selectors = [
                'span.a-price-whole',
                'span.a-offscreen',
                'span.a-price span.a-offscreen',
                '#priceblock_ourprice',
                '#priceblock_dealprice'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    price = self.extract_price(price_text)
                    if price:
                        return price
            
            return None
            
        except Exception as e:
            print(f"Error scraping Amazon price: {e}")
            return None
    
    def scrape_ebay_price(self, product_url: str) -> Optional[float]:
        """Scrape price from eBay"""
        try:
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different price selectors for eBay
            price_selectors = [
                'span[itemprop="price"]',
                '.x-price-primary span',
                '.x-price-original',
                '.x-price-current'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    price = self.extract_price(price_text)
                    if price:
                        return price
            
            return None
            
        except Exception as e:
            print(f"Error scraping eBay price: {e}")
            return None
    
    def scrape_walmart_price(self, product_url: str) -> Optional[float]:
        """Scrape price from Walmart"""
        try:
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different price selectors for Walmart
            price_selectors = [
                'span[data-automation-id="product-price"]',
                '.price-characteristic',
                '.price-main',
                '[data-price-type="finalPrice"]'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    price = self.extract_price(price_text)
                    if price:
                        return price
            
            return None
            
        except Exception as e:
            print(f"Error scraping Walmart price: {e}")
            return None
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None
    
    def get_competitor_prices(self, product_name: str, category: str) -> List[Dict]:
        """Get competitor prices for a product"""
        competitors = []
        
        # Search URLs for different competitors
        search_urls = {
            'amazon': f'https://www.amazon.com/s?k={product_name.replace(" ", "+")}',
            'ebay': f'https://www.ebay.com/sch/i.html?_nkw={product_name.replace(" ", "+")}',
            'walmart': f'https://www.walmart.com/search?q={product_name.replace(" ", "+")}'
        }
        
        for competitor, search_url in search_urls.items():
            try:
                # Add delay to be respectful
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract product URLs (simplified - in real implementation, you'd need more sophisticated parsing)
                product_urls = self.extract_product_urls(soup, competitor)
                
                for url in product_urls[:3]:  # Limit to first 3 results
                    price = None
                    if competitor == 'amazon':
                        price = self.scrape_amazon_price(url)
                    elif competitor == 'ebay':
                        price = self.scrape_ebay_price(url)
                    elif competitor == 'walmart':
                        price = self.scrape_walmart_price(url)
                    
                    if price:
                        competitors.append({
                            'competitor': competitor,
                            'price': price,
                            'url': url
                        })
                        
            except Exception as e:
                print(f"Error getting {competitor} prices: {e}")
                continue
        
        return competitors
    
    def extract_product_urls(self, soup: BeautifulSoup, competitor: str) -> List[str]:
        """Extract product URLs from search results"""
        urls = []
        
        if competitor == 'amazon':
            # Amazon product link selectors
            selectors = [
                'a[href*="/dp/"]',
                'a[data-component-type="s-search-result"]'
            ]
        elif competitor == 'ebay':
            # eBay product link selectors
            selectors = [
                'a[href*="/itm/"]',
                '.s-item__link'
            ]
        elif competitor == 'walmart':
            # Walmart product link selectors
            selectors = [
                'a[href*="/ip/"]',
                '.product-title-link'
            ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and isinstance(href, str):
                    if not href.startswith('http'):
                        href = urljoin(f'https://www.{competitor}.com', href)
                    urls.append(href)
        
        return list(set(urls))  # Remove duplicates 