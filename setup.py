from setuptools import setup, find_packages

setup(
    name="research_analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'flask==3.0.0',
        'qrcode==7.4.2',
        'schedule==1.2.0',
        'scholarly==1.7.11',
        'fpdf==1.7.2',
        'rich==13.3.1',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'matplotlib==3.7.1',
        'transformers==4.35.0',
        'sentencepiece==0.1.99',
    ],
    entry_points={
        'console_scripts': [
            'research-analyzer=research_analyzer.__main__:main',
        ],
    },
    python_requires='>=3.10',
    include_package_data=True,
    package_data={
        'research_analyzer': ['web/templates/*'],
    },
)
