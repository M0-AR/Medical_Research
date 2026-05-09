import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'research_analyzer_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    try:
        # Check environment variables
        required_vars = ['HF_API_KEY', 'SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 
                        'SENDER_PASSWORD', 'ADMIN_EMAIL']
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file")
            sys.exit(1)
            
        # Import and start services based on command line argument
        if len(sys.argv) > 1:
            if sys.argv[1] == 'web':
                from .web.app import app
                app.run(host='0.0.0.0', port=5000)
            elif sys.argv[1] == 'scheduler':
                from .scheduler import run_scheduler
                run_scheduler()
            else:
                logger.error(f"Unknown command: {sys.argv[1]}")
                logger.error("Valid commands are: web, scheduler")
                sys.exit(1)
        else:
            logger.error("Please specify a command: web or scheduler")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
