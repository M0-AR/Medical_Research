import os
import asyncio
from ..utils.medical_scrapers import search_medical_sources
from datetime import datetime
from dotenv import load_dotenv
import time
from ..utils.llm_modules import get_available_models
from .config import SEARCH_TOPICS

# Load environment variables
load_dotenv()

class ResearchPaperAnalyzer:
    def __init__(self, model_names=None):
        self.search_topics = SEARCH_TOPICS['innovations'] + SEARCH_TOPICS['research']
        
        # Initialize LLM models
        available_models = get_available_models()
        self.models = {}
        
        if model_names is None:
            model_names = list(available_models.keys())
            
        for model_name in model_names:
            if model_name in available_models:
                try:
                    self.models[model_name] = available_models[model_name]()
                except Exception as e:
                    print(f"Error loading {model_name}: {e}")
        
        if not self.models:
            raise ValueError("No models were successfully loaded")
        
    async def search_recent_papers(self, days_back=1):
        """Search for recent papers from medical sources."""
        papers = []
        total_papers = 0
        
        print("\n=== Starting Medical Research Search ===")
        for topic in self.search_topics:
            print(f"\nSearching for: {topic}")
            try:
                results = await search_medical_sources(topic, limit_per_source=3)
                
                for paper in results:
                    if paper.get('title') and paper.get('abstract'):
                        papers.append(paper)
                        total_papers += 1
                        print(f"    Found [{paper['source']}]: {paper['title'][:100]}...")
                        
                time.sleep(1)  # Small delay between topics
                
            except Exception as e:
                print(f"    Error searching {topic}: {str(e)[:100]}...")
                continue
        
        print(f"\n=== Search Complete ===")
        print(f"Total papers found: {total_papers}")
        return papers

    def summarize_paper(self, paper):
        """Use multiple LLMs to generate summaries of the paper."""
        summaries = {}
        
        text = f"""
        Title: {paper['title']}
        Abstract: {paper['abstract']}
        Source: {paper.get('source', 'Unknown')}
        Authors: {paper.get('authors', 'Unknown')}
        """
        
        print(f"\nGenerating summaries for: {paper['title'][:100]}...")
        for model_name, model in self.models.items():
            try:
                print(f"  Using {model_name} model...")
                summary = model.summarize(text)
                summaries[f'summary_{model_name}'] = summary
                print(f"    Summary generated: ", summary)
            except Exception as e:
                print(f"    Error with {model_name}: {str(e)[:100]}")
                summaries[f'summary_{model_name}'] = f"Error: {str(e)}"
        
        return summaries

    async def run_analysis(self):
        """Run the complete analysis pipeline."""
        print("\n=== Starting Research Paper Analysis ===")
        
        # Search for papers
        print("\nStep 1: Searching for recent papers...")
        papers = await self.search_recent_papers()
        
        if not papers:
            print("No papers found. Analysis complete.")
            return []
        
        # Process each paper
        print("\nStep 2: Analyzing papers...")
        analyzed_papers = []
        
        for paper in papers:
            try:
                # Generate summaries using different models
                summaries = self.summarize_paper(paper)
                
                # Combine paper data with summaries
                paper_data = {
                    **paper,
                    **summaries,
                    'analysis_date': datetime.now().isoformat()
                }
                
                analyzed_papers.append(paper_data)
                
            except Exception as e:
                print(f"Error analyzing paper: {str(e)}")
                continue
        
        return analyzed_papers
