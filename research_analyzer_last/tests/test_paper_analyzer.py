import pytest
import logging
from src.core.paper_analyzer import ResearchPaperAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_paper_analyzer():
    """Test the paper analyzer with a single paper."""
    # Initialize analyzer
    analyzer = ResearchPaperAnalyzer()
    
    # Test paper query
    query = "Codeveloping an Online Resource for People Bereaved by Suicide: Mixed Methods User-Centered Study"
    
    # Run analysis
    logger.info("Running analysis...")
    analyzed_papers = await analyzer.run_analysis()
    
    assert analyzed_papers is not None
    assert isinstance(analyzed_papers, list)
    
    if analyzed_papers:
        assert 'title' in analyzed_papers[0]
        assert 'abstract' in analyzed_papers[0]
        assert 'source' in analyzed_papers[0]

if __name__ == "__main__":
    print("Running tests...")
    pytest.main([__file__, "-v"])
