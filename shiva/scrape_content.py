import csv
import re
import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def extract_verses_to_json(input_csv_file, output_prefix="output", output_dir="output_files"):
    """
    Reads URLs from the filtered CSV, processes them in batches of 100,
    and saves each batch to a separate JSON file in the specified output directory.

    Args:
        input_csv_file (str): Path to the input CSV file (filtered URLs).
        output_prefix (str): Prefix for output JSON files (e.g., 'output' will generate 'output-1.json', 'output-2.json', etc.)
        output_dir (str): Directory to save output JSON files
    """
    print(f"\n--- Extracting Verses to JSON from '{input_csv_file}' --- ")
    
    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' created/verified")
    except Exception as e:
        print(f"Error creating output directory '{output_dir}': {e}")
        return
    
    # Read all URLs from CSV
    urls_to_process = []
    try:
        with open(input_csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader) # Skip header
                if header != ['URL']:
                     print(f"Warning: CSV header mismatch in {input_csv_file}. Expected ['URL'], got {header}.")
            except StopIteration:
                print(f"Warning: Filtered URL file '{input_csv_file}' is empty.")
                return
            urls_to_process = [row[0] for row in reader if row and row[0].strip()]
    except FileNotFoundError:
        print(f"Error: Filtered URL file '{input_csv_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading filtered CSV '{input_csv_file}': {e}")
        return

    if not urls_to_process:
        print("No URLs found in the filtered file to process.")
        return

    print(f"Found {len(urls_to_process)} URLs to process for verse extraction.")

    # Verse pattern to match the full verse including the number
    verse_pattern = re.compile(r'(.*?॥\s*(\d+)\s*॥)', re.DOTALL)
    script_selection_pattern = re.compile(r'Select script\s*\nHide\s*\nDisplaying in.*?Aksharamukha', re.DOTALL)
    
    # Patterns to identify and remove unwanted content
    unwanted_patterns = [
        re.compile(r'Home\n.*?PRINT', re.DOTALL),  # Navigation elements
        re.compile(r'ITX\n.*?PDF', re.DOTALL),     # Format options
        re.compile(r'^\s*$', re.MULTILINE),        # Empty lines
        re.compile(r'^\s*\n', re.MULTILINE),       # Lines with only whitespace
        re.compile(r'[A-Za-z]', re.MULTILINE),     # English text
    ]

    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = None
    try:
        print("Initializing WebDriver for verse extraction...")
        driver = webdriver.Chrome(options=chrome_options)

        # Process URLs in batches of 100
        batch_size = 100
        total_batches = (len(urls_to_process) + batch_size - 1) // batch_size
        total_processed = 0

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(urls_to_process))
            current_batch = urls_to_process[start_idx:end_idx]
            
            print(f"\nProcessing batch {batch_num + 1}/{total_batches} ({len(current_batch)} URLs)")
            print(f"Processing URLs {start_idx} to {end_idx - 1}")

            batch_verses = []
            for i, url in enumerate(current_batch):
                print(f"Processing URL {i+1}/{len(current_batch)} in batch: {url}")
                try:
                    driver.get(url)
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    # Extract Heading (h2 > h1 > title)
                    heading_tag = soup.find('h2') or soup.find('h1') or soup.title
                    heading = heading_tag.get_text(strip=True) if heading_tag else "Unknown Heading"
                    heading = ' '.join(heading.split()) # Normalize whitespace

                    # Find the main content area - look for divs with Sanskrit text
                    main_content = None
                    for div in soup.find_all('div'):
                        if '॥' in div.get_text():  # Look for verse markers
                            main_content = div
                            break
                    
                    if not main_content:
                        print("  [Warning: No main content area found]")
                        continue

                    # Extract text from main content area
                    body_text = main_content.get_text(separator='\n', strip=True)
                    
                    # Remove script selection text
                    body_text = script_selection_pattern.sub('', body_text)
                    
                    # Remove other unwanted content
                    for pattern in unwanted_patterns:
                        body_text = pattern.sub('', body_text)

                    # Find verses using the marker pattern
                    matches = list(verse_pattern.finditer(body_text))
                    if not matches:
                        print("  [No verse markers found in body text]")
                        continue

                    page_verses = []
                    for match in matches:
                        full_verse = match.group(1).strip()
                        verse_number = match.group(2)
                        
                        # Clean the verse text
                        verse_lines = []
                        for line in full_verse.split('\n'):
                            line = line.strip()
                            # Skip lines that are likely navigation or unwanted content
                            if (line and 
                                not any(word in line.lower() for word in ['home', 'print', 'pdf', 'itx', 'select script']) and
                                not line.isdigit() and  # Skip line numbers
                                not re.match(r'^\s*$', line) and  # Skip empty lines
                                not re.search(r'[A-Za-z]', line)):  # Skip lines with English text
                                verse_lines.append(line)
                        
                        verse_text = '\n'.join(verse_lines)
                        
                        # Remove the verse number from the text
                        verse_text = re.sub(r'॥\s*\d+\s*॥', '', verse_text).strip()
                        
                        if verse_text:
                            # For the first verse, remove the heading if it's present
                            if len(page_verses) == 0 and heading in verse_text:
                                # Split the verse text by newlines and remove lines containing the heading
                                verse_lines = [line for line in verse_text.split('\n') if heading not in line]
                                verse_text = '\n'.join(verse_lines).strip()
                                if not verse_text:  # If nothing left after removing heading
                                    continue
                                
                            ref = f"{heading}.{verse_number}"
                            verse_data = {
                                "ref": ref,
                                "verse": verse_text,
                                "document_link": url
                            }
                            page_verses.append(verse_data)
                            print(f"    Found Verse: {ref}")
                        else:
                            print(f"    Verse {verse_number} marker found, but no text extracted before it.")
                    
                    batch_verses.extend(page_verses)
                    total_processed += 1
                    time.sleep(0.5)

                except TimeoutException:
                    print(f"  [TIMEOUT processing {url}]")
                except Exception as e:
                    print(f"  [ERROR processing {url}: {type(e).__name__} - {e}]")
                    continue

            # Save the current batch to a separate file in the output directory
            if batch_verses:
                output_file = os.path.join(output_dir, f"{output_prefix}-{batch_num + 1}.json")
                try:
                    with open(output_file, 'w', encoding='utf-8') as outfile:
                        json.dump(batch_verses, outfile, ensure_ascii=False, indent=2)
                    print(f"Saved batch {batch_num + 1} to '{output_file}' with {len(batch_verses)} verses")
                except Exception as e:
                    print(f"Error saving batch {batch_num + 1} to '{output_file}': {e}")

    except Exception as e:
        print(f"A critical error occurred during the verse extraction process: {e}")
    finally:
        if driver:
            print("Closing WebDriver...")
            driver.quit()

    # Final summary
    print(f"\nProcessed {total_processed} URLs successfully across {total_batches} batches.")
    print(f"Output files generated in '{output_dir}': {[f'{output_prefix}-{i+1}.json' for i in range(total_batches)]}")

if __name__ == "__main__":
    filtered_input_file = "filtered_urls.csv"
    output_prefix = "output"  # Will generate output-1.json, output-2.json, etc.
    output_dir = "output_files"  # Directory to save output files
    
    print("--- Extracting verses from filtered URLs ---")
    extract_verses_to_json(filtered_input_file, output_prefix, output_dir)
    print("Verse extraction process finished.") 