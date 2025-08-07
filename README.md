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
# Dynamic Solution

## Summary

This tool automates the extraction of data from the Global Burden of Disease (GBD) Results platform, enabling seamless collection of health metrics such as mortality rates and disease prevalence.

## Setup Requirements

### 1. Install Dependencies

Install all required libraries using pip:

```bash
pip install -r requirements.txt
```

### 2. ChromeDriver Setup

**Important:** The Chrome WebDriver in the `selenium` folder **must be compatible** with your current Chrome browser version.

- Check your Chrome version by navigating to `chrome://version/` in your browser
- Download the matching ChromeDriver version from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
- Place the ChromeDriver executable in the `selenium` folder of this project

### 3. API Key Configuration

For AI-assisted filter selection, you must set up an OpenAI API key:

1. Create a `.env` file in the `src` folder
2. Add your OpenAI API key in the following format:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the main script to start the extraction process:

```bash
python main.py
```

The script will:
1. Open the GBD Results website
2. Extract available filters
3. Use AI to determine optimal filter combinations
4. Extract the resulting data
5. Save the data to a CSV file with timestamp

## Project Structure

- `main.py`: Entry point and main workflow
- `extrator.py`: Handles element extraction from the web interface
- `element_types.py`: Defines interactive element classes
- `util.py`: Contains utility functions
- `table_extractor.py`: Extracts tabular data
- `csv_analyzer.py`: Analyzes CSV similarity
