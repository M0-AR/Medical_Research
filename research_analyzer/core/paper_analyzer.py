from scholarly import scholarly
import json
from typing import Dict
import logging
from datetime import datetime
from .llm_modules import get_available_models

class PaperAnalyzer:
    def __init__(self, models=None):
        """Initialize the paper analyzer with specified models."""
        self.models = models or get_available_models()
        self.model_instances = {
            name: model_factory() 
            for name, model_factory in self.models.items()
        }
        
    def fetch_paper(self, query: str) -> Dict:
        """Fetch a paper based on the query."""
        try:
            # Search for the paper using scholarly
            search_query = scholarly.search_pubs(query)
            paper_dict = next(search_query)
            
            # Get detailed information
            paper_details = {
                'title': paper_dict.get('title', ''),
                'abstract': paper_dict.get('abstract', ''),
                'authors': paper_dict.get('author', []),
                'year': paper_dict.get('pub_year', ''),
                'url': paper_dict.get('url', '')
            }
            
            return paper_details
        except Exception as e:
            logging.error(f"Error fetching paper: {str(e)}")
            return {}

    def analyze_paper(self, paper: Dict) -> Dict[str, str]:
        """Analyze the paper using the loaded models."""
        results = {}
        
        text_to_analyze = f"""
        Title: {paper['title']}
        Abstract: {paper['abstract']}
        
        Please analyze this research paper focusing on:
        1. Main findings
        2. Methodology
        3. Implications for the field
        """
        
        for model_name, model in self.model_instances.items():
            try:
                results[model_name] = model.summarize(text_to_analyze)
            except Exception as e:
                logging.error(f"Error analyzing with {model_name}: {str(e)}")
                results[model_name] = f"Analysis failed: {str(e)}"
        
        return results

    def save_results(self, paper: Dict, analysis: Dict[str, str], output_file: str = None):
        """Save the analysis results."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"analysis_results_{timestamp}.json"
        
        results = {
            'paper': paper,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        
        logging.info(f"Results saved to {output_file}")
