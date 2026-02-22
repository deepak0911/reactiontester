from setuptools import setup, find_packages

setup(
    name="competitor-feature-comparison",
    version="1.0.0",
    description="Find top competitors and compare their features using web scraping and Claude API",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.39.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "competitor-compare=src.main:main",
        ],
    },
)
