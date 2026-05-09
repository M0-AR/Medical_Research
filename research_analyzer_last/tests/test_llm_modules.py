import pytest
import os
from dotenv import load_dotenv
import time
from src.models.llm_modules import get_available_models
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

load_dotenv()

class TestLLMModules:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_text = """Title: Novel Treatment for Chronic Pain Using AI-guided Drug Delivery
        
        Abstract: This study presents a breakthrough in chronic pain management using AI-controlled drug delivery systems. 
        The system adapts medication dosage based on real-time patient data, resulting in better pain control and fewer side effects. 
        Clinical trials showed a 45% improvement in pain control compared to traditional methods."""
        
        self.expected_elements = [
            "pain",
            "drug delivery",
            "AI",
            "clinical trials"
        ]
        
        self.models = get_available_models()
        self.console = Console()
    
    def test_model_availability(self):
        """Test if models are available"""
        assert self.models is not None
        assert len(self.models) > 0
        for model_name, model_factory in self.models.items():
            assert hasattr(model_factory, 'name')
            assert hasattr(model_factory, 'generate')
    
    @pytest.mark.asyncio
    async def test_text_generation(self):
        """Test text generation capabilities"""
        for model_name, model_factory in self.models.items():
            llm = model_factory()
            summary = await llm.summarize(self.test_text)
            assert summary is not None
            assert isinstance(summary, str)
            assert len(summary) > 0
            
            # Check if summary contains key elements
            summary_lower = summary.lower()
            found_elements = [elem for elem in self.expected_elements if elem.lower() in summary_lower]
            assert len(found_elements) > 0, f"Summary should contain at least one key element. Found none in: {summary}"

if __name__ == "__main__":
    print("Running tests...")
    pytest.main([__file__, "-v"])
