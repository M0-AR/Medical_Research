# Research Paper Analyzer

A powerful tool for analyzing and summarizing medical research papers from various sources. This project automatically scrapes, analyzes, and generates comprehensive reports from medical research papers across multiple platforms.

## Features

- **Multi-source Data Collection**: Scrapes research papers from:
  - PubMed
  - WHO Publications
  - Clinical Trials
  - MedRxiv

- **Intelligent Analysis**:
  - Automatic paper categorization
  - Topic detection
  - Key findings extraction
  - Research trend analysis

- **Automated Reporting**:
  - PDF report generation
  - Statistical analysis
  - Visual data representation
  - Source distribution analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/research_analyzer_last.git
cd research_analyzer_last
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

1. Copy the `.env.example` file to `.env` and update with your settings:
```bash
cp .env.example .env
```

2. Configure the following in your `.env` file:
   - API keys
   - Email settings
   - Database credentials
   - Other environment-specific variables

3. Update search topics in `config/config.py` if needed.

## Usage

Run the main analysis script:
```bash
python main.py
```

This will:
1. Initialize the research paper analyzer
2. Collect papers from configured sources
3. Analyze the content
4. Generate a comprehensive report

## Project Structure

```
research_analyzer_last/
├── config/               # Configuration files
├── src/                 # Source code
│   ├── core/           # Core analysis logic
│   ├── models/         # ML models and data structures
│   ├── scrapers/       # Data collection modules
│   └── utils/          # Utility functions
├── tests/              # Test files
├── results/            # Generated reports and data
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name
- Contributors

## Acknowledgments

- Medical research institutions
- Open-source community
- Contributors and maintainers
