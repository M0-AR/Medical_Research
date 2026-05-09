from scholarly import scholarly
import logging

class ThesisScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_theses(self, query, limit=10):
        """Search for academic theses."""
        try:
            # Add thesis-specific keywords to the query
            thesis_query = f"{query} thesis OR dissertation"
            search_query = scholarly.search_pubs(thesis_query)
            theses = []
            
            for _ in range(limit):
                try:
                    thesis = next(search_query)
                    if self._is_thesis(thesis):
                        theses.append({
                            'title': thesis.get('title', ''),
                            'abstract': thesis.get('abstract', ''),
                            'author': thesis.get('author', []),
                            'year': thesis.get('pub_year', ''),
                            'url': thesis.get('url', ''),
                            'university': thesis.get('publisher', '')
                        })
                except StopIteration:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing thesis: {str(e)}")
                    continue
            
            return theses
            
        except Exception as e:
            self.logger.error(f"Error searching theses: {str(e)}")
            return []
    
    def _is_thesis(self, pub_data):
        """Check if the publication is likely a thesis/dissertation."""
        if not pub_data:
            return False
            
        title = pub_data.get('title', '').lower()
        pub_type = pub_data.get('pub_type', '').lower()
        venue = pub_data.get('venue', '').lower()
        
        thesis_keywords = ['thesis', 'dissertation', 'doctoral', 'phd', 'master']
        
        return any(keyword in title or keyword in pub_type or keyword in venue 
                  for keyword in thesis_keywords)
