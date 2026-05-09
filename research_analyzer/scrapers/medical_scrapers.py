from scholarly import scholarly
import logging

class MedicalScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_medical_papers(self, query, limit=10):
        """Search for medical research papers."""
        try:
            search_query = scholarly.search_pubs(query)
            papers = []
            
            for _ in range(limit):
                try:
                    paper = next(search_query)
                    papers.append({
                        'title': paper.get('title', ''),
                        'abstract': paper.get('abstract', ''),
                        'authors': paper.get('author', []),
                        'year': paper.get('pub_year', ''),
                        'url': paper.get('url', ''),
                        'citations': paper.get('num_citations', 0)
                    })
                except StopIteration:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing paper: {str(e)}")
                    continue
            
            return papers
            
        except Exception as e:
            self.logger.error(f"Error searching papers: {str(e)}")
            return []
