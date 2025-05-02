# Sanskrit Text Extraction

A collection of scripts to extract Sanskrit texts from the Shiva section of sanskritdocuments.org.

## Overview

This project is broken down into three main scripts:

1. **scrape_urls.py**: Scrapes URLs from the source website
2. **filter_urls.py**: Filters URLs that contain Sanskrit verses
3. **scrape_content.py**: Extracts Sanskrit verses from filtered URLs

There's also a wrapper script (`run_pipeline.py`) that runs all three scripts in sequence.

## Requirements

- Python 3.6+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

### Python Dependencies

```
selenium
beautifulsoup4
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Run the entire pipeline

```bash
python run_pipeline.py
```

This will execute all three scripts in sequence and generate the final output.

### Option 2: Run scripts individually

1. Scrape URLs:
```bash
python scrape_urls.py
```
This will generate `shiva_document_links.csv`.

2. Filter URLs:
```bash
python filter_urls.py
```
This will read from `shiva_document_links.csv` and generate `filtered_urls.csv`.

3. Extract content:
```bash
python scrape_content.py
```
This will read from `filtered_urls.csv` and generate `extracted_verses.json`.

## Output

The final output is a JSON file (`extracted_verses.json`) containing the extracted Sanskrit verses with their references.

## Features

- **URL Scraping**: Efficiently collects all document URLs from the source website
- **URL Filtering**: Identifies pages that contain Sanskrit verses
- **Content Extraction**: Extracts Sanskrit verses while removing unwanted script selection text
- **Error Handling**: Robust error handling throughout the process
- **Progress Reporting**: Detailed progress information during execution

## Notes

- The scripts include delay timers to avoid overloading the source website
- Chrome headless mode is available (commented out) for running without a visible browser
- The content extraction excludes the script selection text 