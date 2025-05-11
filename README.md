# automated-healthcare-data-collection
# Static Solution

## Summary
This code evaluates an array of URLs and returns the most relevant ones according to the prompt given by the user. Then, it summarizes and lists the most relevant topics of the selected links. Finally, it organizes the data in a JSON file.

## Features
- Web scraping of multiple URLs
- Relevance assessment of web page titles based on a user-defined prompt
- Content summarization of relevant pages
- Topic extraction and analysis
- Export results to JSON format

## Requirements
- Python 3.6+
- Internet connection
- OpenAI API key

## Installation
### Libraries that must be installed:
- `requests` - To make HTTP requests to websites
- `beautifulsoup4` - To parse and extract data from HTML (BS4)
- `openai` - To interact with the OpenAI API and use GPT models

**Note:** You can install all these libraries using pip with the following command:
```bash
pip install requests beautifulsoup4 openai
```

## Usage

**Before you start: OpenAI API setup**

Create a file called `API_key.txt` in the same folder as your script and Paste your OpenAI API key into it. The script will read the key automatically.

Example of the contents of the `API_key.txt` file:
```
your_api_key_here
```

Run the script with Python:
```bash
python Code.py
```
