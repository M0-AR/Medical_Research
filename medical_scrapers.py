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
                        id_string = ','.join(ids)
                        params = {
                            'db': 'pubmed',
                            'id': id_string,
                            'retmode': 'xml'
                        }
                        
                        async with session.get(fetch_url, params=params) as fetch_response:
                            if fetch_response.status == 200:
                                articles = []
                                xml_text = await fetch_response.text()
                                root = ET.fromstring(xml_text)
                                
                                for article in root.findall('.//PubmedArticle'):
                                    try:
                                        title = article.find('.//ArticleTitle').text
                                        abstract = article.find('.//Abstract/AbstractText')
                                        abstract = abstract.text if abstract is not None else ""
                                        
                                        authors = []
                                        author_list = article.findall('.//Author')
                                        for author in author_list:
                                            last_name = author.find('LastName')
                                            fore_name = author.find('ForeName')
                                            if last_name is not None and fore_name is not None:
                                                authors.append(f"{fore_name.text} {last_name.text}")
                                        
                                        date_elem = article.find('.//PubDate')
                                        year = date_elem.find('Year')
                                        year = year.text if year is not None else ""
                                        
                                        articles.append({
                                            'title': title,
                                            'abstract': abstract,
                                            'authors': ', '.join(authors),
                                            'year': year,
                                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{ids[0]}/",
                                            'source': 'PubMed'
                                        })
                                    except Exception as e:
                                        print(f"Error parsing PubMed article: {str(e)}")
                                        continue
                                
                                return articles
            except Exception as e:
                print(f"Error in PubMed search: {str(e)}")
                return []
        return []

class ClinicalTrialsScraper(MedicalSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
        
    async def search(self, query, limit=5):
        params = {
            'expr': query,
            'fields': 'NCTId,BriefTitle,BriefSummary,LocationFacility,StartDate,CompletionDate',
            'min_rnk': 1,
            'max_rnk': limit,
            'fmt': 'json'
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        studies = []
                        
                        for study in data.get('StudyFieldsResponse', {}).get('StudyFields', []):
                            try:
                                studies.append({
                                    'title': study.get('BriefTitle', [''])[0],
                                    'abstract': study.get('BriefSummary', [''])[0],
                                    'authors': study.get('LocationFacility', [''])[0],
                                    'year': study.get('StartDate', [''])[0][:4],
                                    'url': f"https://clinicaltrials.gov/ct2/show/{study.get('NCTId', [''])[0]}",
                                    'source': 'ClinicalTrials.gov'
                                })
                            except Exception as e:
                                print(f"Error parsing ClinicalTrials.gov study: {str(e)}")
                                continue
                        
                        return studies
            except Exception as e:
                print(f"Error in ClinicalTrials.gov search: {str(e)}")
                return []
        return []

class MedRxivScraper(MedicalSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.medrxiv.org/details/medrxiv"
        
    async def search(self, query, limit=5):
        params = {
            'q': query,
            'page': 1,
            'size': limit
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = []
                        
                        for paper in data.get('results', []):
                            try:
                                papers.append({
                                    'title': paper.get('title', ''),
                                    'abstract': paper.get('abstract', ''),
                                    'authors': ', '.join(paper.get('authors', [])),
                                    'year': paper.get('date', '')[:4],
                                    'url': paper.get('doi', ''),
                                    'source': 'medRxiv'
                                })
                            except Exception as e:
                                print(f"Error parsing medRxiv paper: {str(e)}")
                                continue
                        
                        return papers
            except Exception as e:
                print(f"Error in medRxiv search: {str(e)}")
                return []
        return []

async def search_medical_sources(query, limit_per_source=5):
    scrapers = [
        PubMedScraper(),
        ClinicalTrialsScraper(),
        MedRxivScraper()
    ]
    
    tasks = [scraper.search(query, limit_per_source) for scraper in scrapers]
    results = await asyncio.gather(*tasks)
    
    # Flatten results from all sources
    all_results = []
    for source_results in results:
        all_results.extend(source_results)
    
    return all_results
