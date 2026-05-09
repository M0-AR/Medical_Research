from scraper import WebScraper
import logging
import os
import sys
import shutil

def setup_output_directory(base_dir):
    """Set up a clean output directory structure"""
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    # Create main directory
    os.makedirs(base_dir)
    
    # Create asset directories
    assets_dir = os.path.join(base_dir, 'assets')
    os.makedirs(os.path.join(assets_dir, 'css'))
    os.makedirs(os.path.join(assets_dir, 'js'))
    os.makedirs(os.path.join(assets_dir, 'images'))
    
    return assets_dir

def create_deployment_config(base_dir):
    """Create deployment configuration files"""
    # Netlify configuration
    netlify_config = """
[build]
  publish = "/"
  command = ""

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
    with open(os.path.join(base_dir, 'netlify.toml'), 'w') as f:
        f.write(netlify_config.strip())
    
    # Add a professional README
    readme_content = """# Website Clone

This is a professional clone of the original website, optimized for deployment.

## Structure
```
.
├── assets/
│   ├── css/     # Stylesheets
│   ├── js/      # JavaScript files
│   └── images/  # Images and media
├── index.html   # Main HTML file
└── netlify.toml # Deployment configuration
```

## Deployment
This website is ready to be deployed to Netlify or any other static hosting service.

## Local Development
To run locally, you can use any static file server:
```bash
npx serve
```
"""
    with open(os.path.join(base_dir, 'README.md'), 'w') as f:
        f.write(readme_content)

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get URL from command line or prompt
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            url = input("Enter website URL: ").strip()
        
        if not url:
            logger.error("No URL provided")
            return
        
        logger.info(f"Starting professional website clone: {url}")
        
        # Initialize scraper
        scraper = WebScraper(url)
        
        # Set up clean output directory
        assets_dir = setup_output_directory(scraper.base_dir)
        
        # Clone website
        data = scraper.clone_website()
        
        if data:
            # Create deployment configuration
            create_deployment_config(scraper.base_dir)
            
            logger.info(f"""
Website cloned successfully!

Assets downloaded:
- Images: {len(data.get("images", []))}
- CSS files: {len(data.get("css_files", []))}
- JavaScript files: {len(data.get("js_files", []))}

Files saved in: {scraper.base_dir}

The website is now ready for deployment!
To test locally:
1. cd {scraper.base_dir}
2. npx serve

To deploy:
1. Push to a Git repository
2. Connect to Netlify or any static hosting service
""")
        
    except KeyboardInterrupt:
        logger.info("Cloning process interrupted by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        if 'scraper' in locals():
            del scraper

if __name__ == '__main__':
    main()
