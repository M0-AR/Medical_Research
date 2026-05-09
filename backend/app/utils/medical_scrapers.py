import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from datetime import datetime
import time
import re
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET

class MedicalSource(ABC):
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    @abstractmethod
    async def search(self, query, limit=5):
        pass

class PubMedScraper(MedicalSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    async def search(self, query, limit=5):
        # First get IDs
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'sort': 'date'
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        text = await response.text()
                        root = ET.fromstring(text)
                        ids = [id_elem.text for id_elem in root.findall('.//Id')]
                        
                        if not ids:
                            return []
                        
                        # Now fetch details for these IDs
                        fetch_url = f"{self.base_url}/efetch.fcgi"
                        params = {
                            'db': 'pubmed',
                            'id': ','.join(ids),
                            'rettype': 'abstract'
                        }
                        
                        papers = []
                        async with session.get(fetch_url, params=params) as fetch_response:
                            if fetch_response.status == 200:
                                content = await fetch_response.text()
                                soup = BeautifulSoup(content, 'xml')
                                
                                for article in soup.find_all('PubmedArticle'):
                                    try:
                                        title = article.find('ArticleTitle').text
                                        abstract = article.find('Abstract')
                                        abstract = abstract.find('AbstractText').text if abstract else "No abstract available"
                                        
                                        # Get authors
                                        authors = []
                                        author_list = article.find('AuthorList')
                                        if author_list:
                                            for author in author_list.find_all('Author'):
                                                last_name = author.find('LastName')
                                                first_name = author.find('ForeName')
                                                if last_name and first_name:
                                                    authors.append(f"{first_name.text} {last_name.text}")
                                        
                                        papers.append({
                                            'title': title,
                                            'abstract': abstract,
                                            'authors': authors,
                                            'source': 'PubMed',
                                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{article.find('PMID').text}/"
                                        })
                                    except Exception as e:
                                        print(f"Error parsing article: {e}")
                                        continue
                                        
                        return papers
                    
            except Exception as e:
                print(f"Error in PubMed search: {e}")
                return []
        
        return []

class ClinicalTrialsScraper(MedicalSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
        
    async def search(self, query, limit=5):
        params = {
            'expr': query,
            'fields': 'BriefTitle,BriefSummary,LocationCountry,NCTId,OfficialTitle',
            'min_rnk': 1,
            'max_rnk': limit,
            'fmt': 'json'
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
                        
                        papers = []
                        for study in studies:
                            title = study.get('BriefTitle', ['No title'])[0]
                            abstract = study.get('BriefSummary', ['No summary'])[0]
                            nct_id = study.get('NCTId', [''])[0]
                            
                            papers.append({
                                'title': title,
                                'abstract': abstract,
                                'authors': [],  # Clinical trials don't typically list authors in the API
                                'source': 'ClinicalTrials.gov',
                                'url': f"https://clinicaltrials.gov/ct2/show/{nct_id}"
                            })
                        
                        return papers
                    
            except Exception as e:
                print(f"Error in ClinicalTrials search: {e}")
                return []
        
        return []

class MedRxivScraper(MedicalSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.medrxiv.org/details/medrxiv"
        
    async def search(self, query, limit=5):
        # Format query for medRxiv API
        formatted_query = query.replace(' ', '%20')
        url = f"{self.base_url}/{formatted_query}/0/0/1/0/1"  # Most recent papers first
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = []
                        
                        for item in data.get('collection', [])[:limit]:
                            papers.append({
                                'title': item.get('title', 'No title'),
                                'abstract': item.get('abstract', 'No abstract available'),
                                'authors': [author.get('name', '') for author in item.get('authors', [])],
                                'source': 'medRxiv',
                                'url': item.get('doi', '')
                            })
                        
                        return papers
                    
            except Exception as e:
                print(f"Error in medRxiv search: {e}")
                return []
        
        return []

async def search_medical_sources(query, limit_per_source=5):
    """Search multiple medical sources concurrently."""
    scrapers = [
        PubMedScraper(),
        ClinicalTrialsScraper(),
        MedRxivScraper()
    ]
    
    tasks = [scraper.search(query, limit_per_source) for scraper in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    papers = []
    for result in results:
        if isinstance(result, list):  # Successful result
            papers.extend(result)
        else:  # Exception occurred
            print(f"Error in one of the scrapers: {result}")
    
    return papers
