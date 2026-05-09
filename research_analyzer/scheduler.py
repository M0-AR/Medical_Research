import schedule
import time
from datetime import datetime
import logging
from core.paper_analyzer import PaperAnalyzer
from core.report_generator import generate_report
from utils.error_handler import handle_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def daily_report_job():
    """Generate daily report at scheduled time"""
    try:
        logger.info(f"Starting daily report generation at {datetime.now()}")
        
        # Initialize analyzer
        analyzer = PaperAnalyzer()
        
        # Get today's papers
        papers = analyzer.fetch_papers()
        if not papers:
            logger.warning("No papers found today")
            return
        
        # Analyze papers with all models
        analysis_results = {}
        for paper in papers:
            try:
                result = analyzer.analyze_paper(paper)
                # Only keep successful analyses
                analysis_results.update({
                    model: summary for model, summary in result.items()
                    if not summary.startswith("Error:")
                })
            except Exception as e:
                logger.error(f"Error analyzing paper: {str(e)}")
                continue
        
        # Generate report with only successful analyses
        report_path = generate_report(papers, analysis_results)
        
        if report_path:
            logger.info(f"Daily report generated successfully: {report_path}")
        else:
            logger.error("Failed to generate daily report")
            
    except Exception as e:
        error_msg = f"Error in daily report job: {str(e)}"
        logger.error(error_msg)
        handle_error(error_msg)

def run_scheduler():
    """Run the scheduler"""
    # Schedule job to run at 2 AM every day
    schedule.every().day.at("02:00").do(daily_report_job)
    
    logger.info("Scheduler started. Will generate reports daily at 2 AM.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
