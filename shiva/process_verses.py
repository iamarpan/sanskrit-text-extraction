#!/usr/bin/env python3
import os
import json
import csv
import re
import time
import glob
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1'
}

def setup_driver():
    """Setup and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    return webdriver.Chrome(options=chrome_options)

def scrape_urls(base_url, output_file="all_urls.csv"):
    """Scrape all URLs from the base URL."""
    print(f"\n--- Scraping URLs from {base_url} ---")
    
    try:
        response = requests.get(base_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        urls = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            if url.startswith('http'):
                urls.append(url)
        
        # Save URLs to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL'])  # Header
            for url in urls:
                writer.writerow([url])
        
        print(f"Found and saved {len(urls)} URLs to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error scraping URLs: {e}")
        return False

def filter_urls(input_file="all_urls.csv", output_file="filtered_urls.csv"):
    """Filter URLs that contain Sanskrit verses."""
    print(f"\n--- Filtering URLs from {input_file} ---")
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header
            urls = [row[0] for row in reader if row and row[0].strip()]
        
        filtered_urls = []
        # Add progress bar and filter for .html URLs
        for url in tqdm(urls, desc="Filtering URLs", unit="url"):
            # Skip if not an HTML file
            if not url.endswith('.html'):
                continue
                
            try:
                response = requests.get(url, headers=HEADERS)
                if '॥' in response.text:  # Check for verse markers
                    filtered_urls.append(url)
            except Exception as e:
                tqdm.write(f"Error processing {url}: {str(e)}")
                continue
        
        # Save filtered URLs
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL'])
            for url in filtered_urls:
                writer.writerow([url])
        
        print(f"\nFound {len(filtered_urls)} URLs containing Sanskrit verses")
        return True
        
    except Exception as e:
        print(f"Error filtering URLs: {e}")
        return False

def extract_verses_from_url(driver, url):
    """Extract verses from a single URL."""
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract Heading
        heading_tag = soup.find('h2') or soup.find('h1') or soup.title
        heading = heading_tag.get_text(strip=True) if heading_tag else "Unknown Heading"
        heading = ' '.join(heading.split())

        # Find main content
        main_content = None
        for div in soup.find_all('div'):
            if '॥' in div.get_text():
                main_content = div
                break
        
        if not main_content:
            return []

        # Extract and clean text
        body_text = main_content.get_text(separator='\n', strip=True)
        body_text = re.sub(r'Select script\s*\nHide\s*\nDisplaying in.*?Aksharamukha', '', body_text, flags=re.DOTALL)
        
        # Remove unwanted content
        unwanted_patterns = [
            r'Home\n.*?PRINT',
            r'ITX\n.*?PDF',
            r'^\s*$',
            r'^\s*\n',
            r'[A-Za-z]'
        ]
        for pattern in unwanted_patterns:
            body_text = re.sub(pattern, '', body_text, flags=re.MULTILINE)

        # Extract verses
        verse_pattern = re.compile(r'(.*?॥\s*(\d+)\s*॥)', re.DOTALL)
        matches = list(verse_pattern.finditer(body_text))
        if not matches:
            return []

        page_verses = []
        for match in matches:
            full_verse = match.group(1).strip()
            verse_number = match.group(2)
            
            # Clean verse text
            verse_lines = []
            for line in full_verse.split('\n'):
                line = line.strip()
                if (line and 
                    not any(word in line.lower() for word in ['home', 'print', 'pdf', 'itx', 'select script']) and
                    not line.isdigit() and
                    not re.match(r'^\s*$', line) and
                    not re.search(r'[A-Za-z]', line)):
                    verse_lines.append(line)
            
            verse_text = '\n'.join(verse_lines)
            verse_text = re.sub(r'॥\s*\d+\s*॥', '', verse_text).strip()
            
            if verse_text:
                if len(page_verses) == 0 and heading in verse_text:
                    verse_lines = [line for line in verse_text.split('\n') if heading not in line]
                    verse_text = '\n'.join(verse_lines).strip()
                    if not verse_text:
                        continue
                
                ref = f"{heading}->{verse_number}"
                verse_data = {
                    "ref": ref,
                    "verse": verse_text,
                    "document_link": url
                }
                page_verses.append(verse_data)

        return page_verses

    except TimeoutException:
        print(f"  [TIMEOUT processing {url}]")
        return []
    except Exception as e:
        print(f"  [ERROR processing {url}: {type(e).__name__} - {e}]")
        return []

def process_urls(input_csv_file, output_dir="output_files", batch_size=100):
    """Process URLs in batches and save to JSON files."""
    print(f"\n--- Processing URLs from '{input_csv_file}' ---")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read URLs
    urls_to_process = []
    try:
        with open(input_csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header
            urls_to_process = [row[0] for row in reader if row and row[0].strip()]
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

    if not urls_to_process:
        print("No URLs found to process")
        return False

    # Process in batches
    driver = setup_driver()
    try:
        total_batches = (len(urls_to_process) + batch_size - 1) // batch_size
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(urls_to_process))
            current_batch = urls_to_process[start_idx:end_idx]
            
            print(f"\nProcessing batch {batch_num + 1}/{total_batches}")
            batch_verses = []
            
            for url in current_batch:
                verses = extract_verses_from_url(driver, url)
                batch_verses.extend(verses)
                time.sleep(0.5)

            # Save batch
            if batch_verses:
                output_file = os.path.join(output_dir, f"output-{batch_num + 1}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(batch_verses, f, ensure_ascii=False, indent=2)
                print(f"Saved batch {batch_num + 1} with {len(batch_verses)} verses")

        return True

    except Exception as e:
        print(f"Error during processing: {e}")
        return False
    finally:
        driver.quit()

def combine_outputs(input_dir="output_files", output_file="output.json"):
    """Combine all batch files into a single output file."""
    print(f"\n--- Combining JSON files from '{input_dir}' ---")
    
    json_files = glob.glob(os.path.join(input_dir, "output-*.json"))
    if not json_files:
        print(f"No JSON files found in '{input_dir}'")
        return False
    
    json_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
    print(f"Found {len(json_files)} JSON files to combine")
    
    all_verses = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                verses = json.load(f)
                all_verses.extend(verses)
                print(f"Added {len(verses)} verses from {os.path.basename(json_file)}")
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_verses, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully combined {len(all_verses)} verses into {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        return False

def main():
    """Main function to run the complete verse processing pipeline."""
    start_time = time.time()
    
    print("\n📋 Sanskrit Verse Processing Pipeline")
    print("-----------------------------------")
    
    # Step 3: Process URLs and create batch files
    if not process_urls("filtered_urls.csv"):
        print("Pipeline stopped due to URL processing failure.")
        return
    
    # Step 4: Combine batch files
    if not combine_outputs():
        print("Pipeline stopped due to output combination failure.")
        return
    
    # Calculate total execution time
    end_time = time.time()
    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    
    print("\n🎉 Complete Sanskrit Verse Processing Pipeline finished successfully!")
    print(f"⏱️ Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds")
    
    # Report output file size
    if os.path.exists("output.json"):
        file_size = os.path.getsize("output.json") / 1024  # Size in KB
        if file_size < 1024:
            print(f"📄 Output file size: {file_size:.2f} KB")
        else:
            print(f"📄 Output file size: {file_size/1024:.2f} MB")

if __name__ == "__main__":
    main() 