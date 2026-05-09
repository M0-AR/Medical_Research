import os
from dotenv import load_dotenv
import time
from llm_modules import get_available_models
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

load_dotenv()

class LLMTester:
    def __init__(self):
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
        self.results = []
        
    def check_summary_quality(self, summary: str) -> tuple[bool, str]:
        """Check if the summary meets quality criteria"""
        if "Error:" in summary:
            return False, "API Error"
            
        summary = summary.lower()
        found_elements = [element for element in self.expected_elements if element in summary]
        if len(found_elements) == 0:
            return False, "No key elements found"
        
        if len(summary.split()) < 10:
            return False, "Summary too short"
            
        return True, f"Found {len(found_elements)} key elements"
        
    def test_models(self):
        """Test all available models and return results"""
        # Create and style the table
        table = Table(title="LLM Models Test Results")
        table.add_column("Model", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        table.add_column("Summary Extract", style="blue")
        
        self.console.print("\n[bold cyan]Starting LLM Models Test...[/bold cyan]\n")
        
        passed_count = 0
        total_count = 0
        
        for model_name, model_factory in self.models.items():
            total_count += 1
            try:
                self.console.print(f"Testing {model_name}...", end="")
                
                # Initialize model
                llm = model_factory()
                
                # Get summary
                start_time = time.time()
                summary = llm.summarize(self.test_text)
                duration = time.time() - start_time
                
                # Check quality
                is_valid, quality_msg = self.check_summary_quality(summary)
                if is_valid:
                    passed_count += 1
                
                # Prepare summary extract
                summary_extract = summary[:100] + "..." if len(summary) > 100 else summary
                
                # Add result to table
                status = "✅ PASS" if is_valid else "❌ FAIL"
                details = f"{quality_msg} ({duration:.1f}s)"
                
                table.add_row(
                    model_name,
                    status,
                    details,
                    summary_extract
                )
                
                self.console.print(" Done!")
                
            except Exception as e:
                table.add_row(
                    model_name,
                    "❌ FAIL",
                    f"Error: {str(e)}",
                    "N/A"
                )
                self.console.print(" Error!")
        
        # Print results
        self.console.print("\n[bold]Test Results:[/bold]")
        self.console.print(table)
        
        # Print summary in a panel
        summary_text = f"""
[bold]Total Models:[/bold] {total_count}
[bold green]Passed:[/bold green] {passed_count}
[bold red]Failed:[/bold red] {total_count - passed_count}
[bold yellow]Success Rate:[/bold yellow] {(passed_count/total_count)*100:.1f}%
        """
        
        self.console.print(Panel(
            summary_text,
            title="[bold]Summary[/bold]",
            border_style="blue"
        ))
        
        if not os.getenv('HF_API_KEY'):
            self.console.print(Panel(
                "[bold red]HF_API_KEY not set in environment variables![/bold red]",
                border_style="red"
            ))

def main():
    tester = LLMTester()
    tester.test_models()

if __name__ == "__main__":
    main()
