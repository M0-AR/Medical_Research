from setuptools import setup, find_packages

setup(
    name="research_analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'requests',
        'python-dotenv',
        'tqdm',
        'beautifulsoup4',
        'lxml',
        'aiohttp',
        'fake-useragent',
        'fpdf2',
        'matplotlib',
        'torch',
        'transformers',
        'sentencepiece',
        'pytest',
        'pytest-asyncio'
    ]
)
