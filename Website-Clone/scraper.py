import requests
from bs4 import BeautifulSoup
import os
import time
import re
import config
from urllib.parse import urljoin, urlparse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime
import json
import shutil

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        
        # Set up base directory
        self.base_dir = os.path.join('website_clone')
        
        # Set up asset directories
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        self.images_dir = os.path.join(self.assets_dir, 'images')
        self.css_dir = os.path.join(self.assets_dir, 'css')
        self.js_dir = os.path.join(self.assets_dir, 'js')
        
        # Clean up old files
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
        
        # Create directories
        os.makedirs(self.base_dir)
        os.makedirs(self.images_dir)
        os.makedirs(self.css_dir)
        os.makedirs(self.js_dir)
        
        # Set up logging
        log_file = os.path.join(self.base_dir, 'scraping.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Set up requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def save_metadata(self, data):
        """Save metadata to JSON file"""
        metadata = {
            'url': self.base_url,
            'domain': self.domain,
            'scrape_date': datetime.now().isoformat(),
            'stats': {
                'images_count': len(data.get('images', [])),
                'headers_count': len(data.get('headers', [])),
                'paragraphs_count': len(data.get('paragraphs', [])),
                'links_count': len(data.get('links', [])),
            },
            'data': data
        }
        
        metadata_file = os.path.join(self.base_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f'Metadata saved to: {metadata_file}')

    def save_text_content(self, data):
        """Save text content to separate files"""
        # Save headers
        headers_file = os.path.join(self.base_dir, 'headers.txt')
        with open(headers_file, 'w', encoding='utf-8') as f:
            for header in data.get('headers', []):
                if header and not header.isspace():
                    f.write(f'{header}\n')
        
        # Save paragraphs
        paragraphs_file = os.path.join(self.base_dir, 'paragraphs.txt')
        with open(paragraphs_file, 'w', encoding='utf-8') as f:
            for para in data.get('paragraphs', []):
                if para and not para.isspace():
                    f.write(f'{para}\n\n')
        
        # Save links
        links_file = os.path.join(self.base_dir, 'links.txt')
        with open(links_file, 'w', encoding='utf-8') as f:
            for link in data.get('links', []):
                if link and not link.isspace():
                    f.write(f'{link}\n')

    def download_file(self, url, local_path):
        """Download a file and save it locally"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                self.logger.error(f"Failed to download {url}: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            return False

    def process_css(self, css_url):
        """Process and download CSS file"""
        try:
            response = requests.get(css_url)
            if response.status_code == 200:
                css_content = response.text
                
                # Fix relative URLs in CSS
                css_content = css_content.replace('url(/', f'url({self.base_url}/')
                css_content = css_content.replace('url("./', 'url("' + self.base_url)
                css_content = css_content.replace("url('./", 'url(\'' + self.base_url)
                
                # Save CSS file
                css_name = os.path.basename(urlparse(css_url).path) or 'style.css'
                css_path = os.path.join(self.css_dir, css_name)
                os.makedirs(os.path.dirname(css_path), exist_ok=True)
                
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                self.logger.info(f"Saved CSS file: {css_name}")
                return css_path
            else:
                self.logger.error(f"Failed to download CSS {css_url}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error processing CSS {css_url}: {str(e)}")
            return None

    def process_javascript(self, js_url):
        """Process and download JavaScript file"""
        try:
            response = requests.get(js_url)
            if response.status_code == 200:
                js_content = response.text
                
                # Save JavaScript file
                js_name = os.path.basename(urlparse(js_url).path) or 'script.js'
                js_path = os.path.join(self.js_dir, js_name)
                os.makedirs(os.path.dirname(js_path), exist_ok=True)
                
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                
                self.logger.info(f"Saved JavaScript file: {js_name}")
                return js_path
            else:
                self.logger.error(f"Failed to download JavaScript {js_url}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error processing JavaScript {js_url}: {str(e)}")
            return None

    def download_images(self):
        """Download and save images"""
        downloaded = 0
        self.image_urls = self.get_image_urls(BeautifulSoup(self.driver.page_source, 'html.parser'))
        for img_url in self.image_urls:
            try:
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(self.base_url, img_url)
                
                img_name = os.path.basename(urlparse(img_url).path)
                if not img_name:
                    img_name = 'image_' + str(downloaded + 1) + '.jpg'
                
                img_path = os.path.join(self.images_dir, img_name)
                
                if self.download_file(img_url, img_path):
                    downloaded += 1
                    self.logger.info(f"Saved: {img_name}")
            except Exception as e:
                self.logger.error(f"Unexpected error downloading {img_url}: {str(e)}")
        
        self.logger.info(f"Successfully downloaded {downloaded} images")
        return downloaded

    def scrape(self):
        """Extract all data from the website"""
        try:
            # Download images
            images = self.download_images()
            
            # Extract text content
            self.driver.get(self.base_url)
            self.wait_for_page_load()
            self.scroll_page()
            
            # Wait for dynamic content
            time.sleep(2)
            
            # Get page source after JavaScript execution
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract text content
            text_content = self.extract_text_content(soup)
            
            data = {
                'headers': text_content['headers'],
                'paragraphs': text_content['paragraphs'],
                'links': text_content['links'],
                'images': images
            }
            
            # Save data
            self.save_metadata(data)
            self.save_text_content(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f'Error extracting data: {str(e)}')
            return None

    def wait_for_page_load(self):
        """Wait for the page to load completely"""
        try:
            self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(3)
        except Exception as e:
            self.logger.warning(f"Error waiting for page load: {str(e)}")

    def scroll_page(self):
        """Scroll the page to load dynamic content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            self.logger.warning(f"Error scrolling page: {str(e)}")

    def extract_text_content(self, soup):
        """Extract text content from the page with better handling of dynamic content"""
        # Extract headers
        headers = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            # Remove any script or style elements
            for element in h.find_all(['script', 'style']):
                element.decompose()
            text = h.get_text(strip=True, separator=' ')
            if text and not text.isspace():
                headers.append(text)

        # Extract paragraphs from various content containers
        paragraphs = []
        content_selectors = [
            'p', 'article', 'section', '.content', '.text',
            '[class*="content"]', '[class*="text"]', '[class*="body"]',
            'div > p', 'main p', 'article p'
        ]
        
        for selector in content_selectors:
            for element in soup.select(selector):
                # Skip if parent is already processed
                if any(p in paragraphs for p in element.parents):
                    continue
                    
                # Remove any script, style, or nav elements
                for unwanted in element.find_all(['script', 'style', 'nav']):
                    unwanted.decompose()
                    
                text = element.get_text(strip=True, separator=' ')
                if text and not text.isspace() and len(text) > 20:  # Minimum length to filter noise
                    if text not in paragraphs:  # Avoid duplicates
                        paragraphs.append(text)

        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and not href.startswith('#') and href != '/':
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(self.base_url, href)
                if href not in links:  # Avoid duplicates
                    links.append(href)

        return {
            'headers': headers,
            'paragraphs': paragraphs,
            'links': links
        }

    @staticmethod
    def sanitize_filename(name):
        # Get file extension if exists
        name, ext = os.path.splitext(name)
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Ensure the filename is not empty
        if not name:
            name = 'image'
        return (name + ext).strip()

    def get_image_urls(self, soup):
        image_urls = set()
        
        try:
            # Wait for images to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            
            # 1. Find all image elements
            selectors = [
                'img[src]', 'img[data-src]', 'img[data-original]',
                'div[style*="background-image"]', 'div[data-bg]',
                'picture source[srcset]'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Check multiple attributes
                    for attr in ['src', 'data-src', 'data-original', 'srcset', 'data-bg']:
                        value = element.get_attribute(attr)
                        if value:
                            if ',' in value:  # Handle srcset
                                urls = value.split(',')
                                for url in urls:
                                    image_url = url.strip().split(' ')[0]
                                    image_urls.add(image_url)
                            else:
                                image_urls.add(value)
                    
                    # Check background image
                    style = element.get_attribute('style')
                    if style and 'background-image' in style:
                        urls = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
                        image_urls.update(urls)

            # 2. Execute JavaScript to find hidden images
            js_images = self.driver.execute_script("""
                var images = [];
                var elements = document.getElementsByTagName('*');
                for (var i = 0; i < elements.length; i++) {
                    var style = window.getComputedStyle(elements[i], null);
                    var bg = style.backgroundImage;
                    if (bg && bg !== 'none') images.push(bg);
                }
                return images;
            """)
            
            for img in js_images:
                urls = re.findall(r'url\(["\']?(.*?)["\']?\)', img)
                image_urls.update(urls)

        except Exception as e:
            self.logger.error(f"Error extracting images: {str(e)}")

        return image_urls

    def clone_website(self):
        """Clone the website with all files"""
        try:
            self.logger.info(f"Starting website clone: {self.base_url}")
            
            # Load the page
            self.driver.get(self.base_url)
            self.wait_for_page_load()
            self.scroll_page()
            
            # Get page content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Process stylesheets
            css_files = []
            for css in soup.find_all('link', rel='stylesheet'):
                if css_url := css.get('href'):
                    if not css_url.startswith(('http://', 'https://')):
                        css_url = urljoin(self.base_url, css_url)
                    if css_path := self.process_css(css_url):
                        css_files.append(css_path)
                        css['href'] = os.path.join('css', os.path.basename(css_path))
            
            # Process JavaScript files
            js_files = []
            for script in soup.find_all('script', src=True):
                if js_url := script.get('src'):
                    if not js_url.startswith(('http://', 'https://')):
                        js_url = urljoin(self.base_url, js_url)
                    if js_path := self.process_javascript(js_url):
                        js_files.append(js_path)
                        script['src'] = os.path.join('js', os.path.basename(js_path))
            
            # Get image URLs
            self.image_urls = self.get_image_urls(soup)
            
            # Download images
            downloaded_images = self.download_images()
            
            # Update image paths in HTML
            for img in soup.find_all('img'):
                if src := img.get('src'):
                    img_name = os.path.basename(urlparse(src).path)
                    img['src'] = os.path.join('images', img_name)
            
            # Save the modified HTML
            index_path = os.path.join(self.base_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            # Combine CSS and JavaScript files
            self.combine_css_files(css_files)
            self.combine_js_files(js_files)
            
            self.logger.info("Website cloned successfully!")
            
            return {
                'images': self.image_urls,
                'css_files': css_files,
                'js_files': js_files
            }
            
        except Exception as e:
            self.logger.error(f"Error cloning website: {str(e)}")
            return None

    def combine_css_files(self, css_files):
        """Combine all CSS files into one file"""
        combined_css = os.path.join(self.css_dir, 'styles.css')
        
        with open(combined_css, 'w', encoding='utf-8') as outfile:
            for css_file in css_files:
                if os.path.exists(css_file):
                    with open(css_file, 'r', encoding='utf-8') as infile:
                        outfile.write(f'/* From {os.path.basename(css_file)} */\n')
                        outfile.write(infile.read())
                        outfile.write('\n\n')
        
        self.logger.info('Combined all CSS files into styles.css')
        return 'assets/css/styles.css'

    def combine_js_files(self, js_files):
        """Combine all JavaScript files into one file"""
        combined_js = os.path.join(self.js_dir, 'script.js')
        
        with open(combined_js, 'w', encoding='utf-8') as outfile:
            for js_file in js_files:
                if os.path.exists(js_file):
                    with open(js_file, 'r', encoding='utf-8') as infile:
                        outfile.write(f'// From {os.path.basename(js_file)}\n')
                        outfile.write(infile.read())
                        outfile.write('\n\n')
        
        self.logger.info('Combined all JavaScript files into script.js')
        return 'assets/js/script.js'
