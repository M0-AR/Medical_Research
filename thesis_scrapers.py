import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import json
from datetime import datetime
import time
import re

class ThesisSource:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

class OATDScraper(ThesisSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://oatd.org"
        
    async def search(self, query, limit=5):
        url = f"{self.base_url}/search?q={query}&form=basic"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    results = []
                    
                    for item in soup.select('.result-item')[:limit]:
                        try:
                            title = item.select_one('.title').text.strip()
                            abstract = item.select_one('.abstract').text.strip() if item.select_one('.abstract') else ""
                            author = item.select_one('.author').text.strip() if item.select_one('.author') else ""
                            university = item.select_one('.university').text.strip() if item.select_one('.university') else ""
                            year = item.select_one('.year').text.strip() if item.select_one('.year') else ""
                            url = self.base_url + item.select_one('.title a')['href'] if item.select_one('.title a') else ""
                            
                            results.append({
                                'title': title,
                                'abstract': abstract,
                                'authors': author,
                                'university': university,
                                'year': year,
                                'url': url,
                                'source': 'OATD'
                            })
                        except Exception as e:
                            print(f"Error parsing OATD result: {str(e)}")
                            continue
                            
                    return results
        return []

class CoreScraper(ThesisSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://core.ac.uk/search/"
        
    async def search(self, query, limit=5):
        url = f"{self.base_url}?q={query}%20thesis&type=thesis"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    results = []
                    
                    for item in soup.select('.search-result')[:limit]:
                        try:
                            title = item.select_one('.title').text.strip()
                            abstract = item.select_one('.abstract').text.strip() if item.select_one('.abstract') else ""
                            authors = item.select_one('.authors').text.strip() if item.select_one('.authors') else ""
                            university = item.select_one('.publisher').text.strip() if item.select_one('.publisher') else ""
                            year = re.search(r'\b\d{4}\b', item.text)
                            year = year.group(0) if year else ""
                            url = item.select_one('.title a')['href'] if item.select_one('.title a') else ""
                            
                            results.append({
                                'title': title,
                                'abstract': abstract,
                                'authors': authors,
                                'university': university,
                                'year': year,
                                'url': url,
                                'source': 'CORE'
                            })
                        except Exception as e:
                            print(f"Error parsing CORE result: {str(e)}")
                            continue
                            
                    return results
        return []

class DartEuropeScraper(ThesisSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.dart-europe.org/basic-search.php"
        
    async def search(self, query, limit=5):
        params = {
            'kw[]': query,
            'f': 'n',
            'pb': 'y',
            'sort': 'title'
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    results = []
                    
                    for item in soup.select('.record')[:limit]:
                        try:
                            title = item.select_one('.title').text.strip()
                            abstract = item.select_one('.abstract').text.strip() if item.select_one('.abstract') else ""
                            author = item.select_one('.author').text.strip() if item.select_one('.author') else ""
                            university = item.select_one('.institution').text.strip() if item.select_one('.institution') else ""
                            year = item.select_one('.year').text.strip() if item.select_one('.year') else ""
                            url = item.select_one('.title a')['href'] if item.select_one('.title a') else ""
                            
                            results.append({
                                'title': title,
                                'abstract': abstract,
                                'authors': author,
                                'university': university,
                                'year': year,
                                'url': url,
                                'source': 'DART-Europe'
                            })
                        except Exception as e:
                            print(f"Error parsing DART-Europe result: {str(e)}")
                            continue
                            
                    return results
        return []

async def search_all_sources(query, limit_per_source=3):
    scrapers = [
        OATDScraper(),
        CoreScraper(),
        DartEuropeScraper()
    ]
    
    tasks = [scraper.search(query, limit_per_source) for scraper in scrapers]
    results = await asyncio.gather(*tasks)
    
    # Flatten results from all sources
    all_results = []
    for source_results in results:
        all_results.extend(source_results)
    
    return all_results
