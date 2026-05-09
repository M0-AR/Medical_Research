# Research Paper Analyzer

A Python package for analyzing research papers using multiple LLM models.

## Project Structure

```
research_analyzer/
├── core/                  # Core functionality
│   ├── llm_modules.py    # LLM model implementations
│   └── paper_analyzer.py # Paper analysis logic
├── scrapers/             # Web scraping modules
│   ├── medical_scrapers.py
│   └── thesis_scrapers.py
├── tests/                # Test modules
│   ├── test_llm_modules.py
│   └── test_paper_analyzer.py
└── utils/                # Utility functions
```

## Features

- Searches for and analyzes research papers from top universities
- Uses multiple LLM models through Hugging Face's API:
  - FLAN-T5-XXL (General purpose)
  - PEGASUS (Abstractive summarization)
  - LED (Long document summarization)
  - Mistral-7B (General purpose)
  - BLOOMZ (Multilingual)
  - And more...
- Specialized scrapers for medical papers and theses
- Comprehensive testing suite for model evaluation

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Hugging Face API key:
```bash
# Create .env file and add your API key
echo "HF_API_KEY=your_api_key_here" > .env
```

## Usage

### Testing LLM Models

Run the LLM model test suite:
```bash
python -m research_analyzer.tests.test_llm_modules
```

### Analyzing Papers

Run the paper analyzer test:
```bash
python -m research_analyzer.tests.test_paper_analyzer
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
