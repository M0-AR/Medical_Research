import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
import shutil
import sys

class PreciseWebsiteCloner:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.output_dir = 'website_clone'
        
        # Create clean output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
        # Create asset directories
        self.assets_dir = os.path.join(self.output_dir, 'assets')
        os.makedirs(os.path.join(self.assets_dir, 'css'))
        os.makedirs(os.path.join(self.assets_dir, 'js'))
        os.makedirs(os.path.join(self.assets_dir, 'images'))
        
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def download_file(self, url, local_path):
        """Download a file and save it locally"""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
        return False

    def process_css(self, css_url):
        """Download and process CSS file"""
        try:
            response = requests.get(css_url)
            if response.status_code == 200:
                css_content = response.text
                # Fix relative URLs in CSS
                css_content = css_content.replace('url(/', f'url({self.url}/')
                return css_content
        except Exception as e:
            self.logger.error(f"Error processing CSS {css_url}: {str(e)}")
        return None

    def clone(self):
        """Clone the website precisely"""
        try:
            self.logger.info(f"Starting precise clone of {self.url}")
            
            # Get the page content
            self.driver.get(self.url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Process stylesheets
            for css_link in soup.find_all('link', rel='stylesheet'):
                if css_url := css_link.get('href'):
                    if not css_url.startswith(('http://', 'https://')):
                        css_url = urljoin(self.url, css_url)
                    
                    css_name = os.path.basename(urlparse(css_url).path)
                    css_path = os.path.join(self.assets_dir, 'css', css_name or 'style.css')
                    
                    if css_content := self.process_css(css_url):
                        with open(css_path, 'w', encoding='utf-8') as f:
                            f.write(css_content)
                        css_link['href'] = f'assets/css/{os.path.basename(css_path)}'
            
            # Process scripts
            for script in soup.find_all('script', src=True):
                if script_url := script.get('src'):
                    if not script_url.startswith(('http://', 'https://')):
                        script_url = urljoin(self.url, script_url)
                    
                    script_name = os.path.basename(urlparse(script_url).path)
                    script_path = os.path.join(self.assets_dir, 'js', script_name or 'script.js')
                    
                    if self.download_file(script_url, script_path):
                        script['src'] = f'assets/js/{os.path.basename(script_path)}'
            
            # Process images
            for img in soup.find_all('img'):
                if img_url := img.get('src'):
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(self.url, img_url)
                    
                    img_name = os.path.basename(urlparse(img_url).path)
                    img_path = os.path.join(self.assets_dir, 'images', img_name or 'image.jpg')
                    
                    if self.download_file(img_url, img_path):
                        img['src'] = f'assets/images/{os.path.basename(img_path)}'
            
            # Save the modified HTML
            index_path = os.path.join(self.output_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            # Create a simple deployment configuration
            netlify_config = """
[build]
  publish = "/"
  command = ""

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
            with open(os.path.join(self.output_dir, 'netlify.toml'), 'w') as f:
                f.write(netlify_config.strip())
            
            self.logger.info("Website cloned successfully!")
            
        except Exception as e:
            self.logger.error(f"Error cloning website: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    import sys
    
    # Default URL if none provided
    url = "https://pcb-factory-wwcjm2h.gamma.site/"
    
    # Allow URL to be passed as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    try:
        cloner = PreciseWebsiteCloner(url)
        cloner.clone()
    except Exception as e:
        logging.error(f"Failed to clone website: {str(e)}")
        sys.exit(1)
