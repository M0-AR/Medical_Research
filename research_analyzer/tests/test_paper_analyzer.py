from ..core.paper_analyzer import PaperAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the paper analyzer with a single paper."""
    # Initialize analyzer
    analyzer = PaperAnalyzer()
    
    # Test paper query
    query = "Codeveloping an Online Resource for People Bereaved by Suicide: Mixed Methods User-Centered Study"
    
    # Fetch paper
    logger.info("Fetching paper...")
    paper = analyzer.fetch_paper(query)
    
    if not paper:
        logger.error("Failed to fetch paper")
        return
    
    # Analyze paper
    logger.info("Analyzing paper...")
    analysis_results = analyzer.analyze_paper(paper)
    
    # Save results with test prefix
    analyzer.save_results(paper, analysis_results, "test_analysis_results.json")
    
    logger.info("Test analysis complete!")

if __name__ == "__main__":
    main()
