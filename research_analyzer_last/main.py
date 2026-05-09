import asyncio
from src.core.paper_analyzer import ResearchPaperAnalyzer
from src.utils.report_generator import generate_report
import os

async def main():
    try:
        # Initialize the analyzer
        print("Initializing Research Paper Analyzer...")
        analyzer = ResearchPaperAnalyzer()
        
        # Run analysis
        print("\nStarting analysis...")
        analyzed_papers = await analyzer.run_analysis()
        
        if analyzed_papers:
            # Generate report
            print("\nGenerating report...")
            report_file = generate_report(analyzed_papers)
            
            if report_file:
                print(f"\nSuccess! Report generated at: {report_file}")
            else:
                print("\nError: Failed to generate report")
        else:
            print("\nNo papers were analyzed. Please check your internet connection and try again.")
            
    except Exception as e:
        print(f"\nError during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
