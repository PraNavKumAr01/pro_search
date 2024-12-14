from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pro-search",
    version="0.1.3",
    author="Pranav Kumar",
    author_email="pranavkumarnair@gmail.com",
    description="An advanced web search package combining AI and web scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PraNavKumAr01/pro_search",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "groq",
    ],
)
