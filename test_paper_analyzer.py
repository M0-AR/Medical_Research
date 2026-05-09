from scholarly import scholarly
import json
from typing import Dict
import logging
from datetime import datetime
from llm_modules import get_available_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPaperAnalyzer:
    def __init__(self):
        """Initialize the test paper analyzer with Mistral model."""
        self.models = get_available_models()
        self.model_instances = {
            name: model_factory() 
            for name, model_factory in self.models.items()
        }
        logger.info(f"Initialized with models: {list(self.models.keys())}")

    def fetch_paper(self) -> Dict:
        """Fetch a specific paper about digital bereavement support."""
        try:
            # Search for a specific paper using scholarly
            search_query = scholarly.search_pubs(
                "Codeveloping an Online Resource for People Bereaved by Suicide: Mixed Methods User-Centered Study"
            )
            paper_dict = next(search_query)
            
            # Get detailed information
            paper_details = {
                'title': paper_dict.get('title', ''),
                'abstract': paper_dict.get('abstract', ''),
                'authors': paper_dict.get('author', []),
                'year': paper_dict.get('pub_year', ''),
                'url': paper_dict.get('url', '')
            }
            
            # If abstract is missing, add a default one for testing
            if not paper_details['abstract']:
                paper_details['abstract'] = """
                Although suicide bereavement is highly distressing and is associated with an increased risk of suicidal behaviors 
                and mental and physical health impairments, those bereaved by suicide encounter difficulties accessing support. 
                Digital resources offer new forms of support for bereaved people. However, digital resources dedicated to those 
                bereaved by suicide are still limited. This study aimed to codevelop an online resource for people bereaved by suicide.
                """
            
            return paper_details
        except Exception as e:
            logger.error(f"Error fetching paper: {str(e)}")
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
        3. Implications for digital bereavement support
        """
        
        for model_name, model in self.model_instances.items():
            try:
                results[model_name] = model.summarize(text_to_analyze)
            except Exception as e:
                logger.error(f"Error analyzing with {model_name}: {str(e)}")
                results[model_name] = f"Analysis failed: {str(e)}"
        
        return results

    def save_results(self, paper: Dict, analysis: Dict[str, str]):
        """Save the analysis results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_analysis_results_{timestamp}.json"
        
        results = {
            'paper': paper,
            'analysis': analysis,
            'timestamp': timestamp
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        
        logger.info(f"Results saved to {output_file}")

def main():
    """Main function to run the test."""
    # Initialize analyzer
    analyzer = TestPaperAnalyzer()
    
    # Fetch paper
    logger.info("Fetching paper...")
    paper = analyzer.fetch_paper()
    
    if not paper:
        logger.error("Failed to fetch paper")
        return
    
    # Analyze paper
    logger.info("Analyzing paper...")
    analysis_results = analyzer.analyze_paper(paper)
    
    # Save results
    analyzer.save_results(paper, analysis_results)
    
    logger.info("Test analysis complete!")

if __name__ == "__main__":
    main()
