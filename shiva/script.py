import csv
from urllib.parse import urljoin
import re # Import regex module
import time # Import time for delays
import json # Import JSON module
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Define a common browser User-Agent (might not be strictly needed with Selenium, but doesn't hurt)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_shiva_links(url, output_csv_file):
    """
    Scrapes specific links from the given URL using Selenium to handle dynamic content,
    and saves them to a CSV file.

    Args:
        url (str): The URL of the webpage to scrape.
        output_csv_file (str): The name of the CSV file to save the links to.
    """
    extracted_links = []
    
    # Setup Chrome options (optional, e.g., for headless mode)
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Uncomment to run Chrome in the background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={headers['User-Agent']}") # Set user agent via options

    # Specify path to chromedriver if it's not in PATH (optional)
    # service = Service('/path/to/chromedriver') 
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver = None # Initialize driver to None
    try:
        # Initialize WebDriver (assumes chromedriver is in PATH)
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)

        # Wait up to 20 seconds for the list items with class 'devanagari' to be present
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.devanagari")))

        # Get the page source after waiting for elements
        page_source = driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the specific UL tag
        target_ul = soup.find('ul', style='list-style-type:none')

        if not target_ul:
            print("Error: Could not find the target UL tag (<ul style='list-style-type:none'>)")
            return

        # Find all list items with class="devanagari" within the target UL
        list_items = target_ul.find_all('li', class_='devanagari')

        if not list_items:
            print(f"No list items with class 'devanagari' found within the target UL on {url} after waiting.")
            return

        # Iterate through the found list items
        for item in list_items:
            # Find all anchor tags within the current list item
            anchor_tags = item.find_all('a')

            # Check if there are at least 3 anchor tags
            if len(anchor_tags) >= 3:
                # Get the href attribute of the third anchor tag (index 2)
                third_anchor = anchor_tags[2]
                href = third_anchor.get('href')

                if href:
                    # Resolve the URL (handles both absolute and relative URLs)
                    full_url = urljoin(url, href)
                    extracted_links.append(full_url)

        # Write the extracted links to a CSV file
        if extracted_links:
            with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['URL']) # Write header
                writer.writerows([[link] for link in extracted_links]) # Write links
            print(f"Successfully scraped {len(extracted_links)} links and saved them to '{output_csv_file}'")
        else:
            print("No links found matching the criteria (3rd 'a' tag in 'li.devanagari').")

    except TimeoutException:
        print(f"Error: Timed out waiting for 'li.devanagari' elements to load on {url}")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        # Ensure the browser is closed even if errors occur
        if driver:
            driver.quit()

def filter_urls_by_verse_pattern(input_csv_file, output_csv_file):
    """
    Reads URLs from an input CSV, visits each URL, checks for a verse pattern (|| number ||),
    and saves matching URLs to an output CSV.

    Args:
        input_csv_file (str): Path to the input CSV file containing URLs.
        output_csv_file (str): Path to the output CSV file for filtered URLs.
    """
    print(f"\nStarting filtering process: Reading from '{input_csv_file}'")
    urls_to_check = []
    try:
        with open(input_csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader) # Skip header row
                if header != ['URL']:
                    print(f"Warning: Expected header ['URL'] in {input_csv_file}, found {header}. Attempting to read first column anyway.")
                    # Reset reader to beginning if header mismatch
                    infile.seek(0)
                    # Decide if you want to skip the actual first line if it was a wrong header
                    # next(reader) # Optional: uncomment if the first line IS a header, just not 'URL'
            except StopIteration: # Handle empty file
                print(f"Warning: Input file '{input_csv_file}' is empty or has no header.")
                return # Cannot proceed if file is empty
            
            urls_to_check = [row[0] for row in reader if row and row[0].strip()] # Read URLs from the first column, ensure not empty

    except FileNotFoundError:
        print(f"Error: Input file '{input_csv_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading input CSV '{input_csv_file}': {e}")
        return

    if not urls_to_check:
        print("No valid URLs found in the input file to filter.")
        return

    print(f"Found {len(urls_to_check)} URLs to check.")
    filtered_urls = []
    verse_pattern = re.compile(r'॥\s*\d+\s*॥') # Compile regex for efficiency

    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Keep headless commented out for now
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = None
    try:
        print("Initializing WebDriver for filtering...")
        # Ensure chromedriver is in PATH or specify service=Service('/path/to/chromedriver')
        driver = webdriver.Chrome(options=chrome_options)
        
        for i, url in enumerate(urls_to_check):
            print(f"Checking URL {i+1}/{len(urls_to_check)}: {url}", end=' ')
            try:
                driver.get(url)
                # Wait for body tag to ensure basic page load
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # More robust text extraction - combine sources
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                
                if verse_pattern.search(page_text):
                    print("[MATCH FOUND]")
                    filtered_urls.append(url)
                else:
                    print("[No Match]")
                
                time.sleep(1) # 1-second delay between requests

            except TimeoutException:
                print(f"[TIMEOUT waiting for body on {url}]")
            except Exception as e:
                # Log specific error for the URL but continue
                print(f"[ERROR processing {url}: {type(e).__name__} - {e}]")
                # Consider adding the problematic URL to a separate error log if needed
                continue # Skip to the next URL

    except Exception as e:
        # Catch broader errors like WebDriver initialization failure
        print(f"An critical error occurred during the filtering process: {e}")
    finally:
        if driver:
            print("Closing WebDriver...")
            driver.quit()

    # Write the filtered URLs to the output CSV file
    if filtered_urls:
        print(f"\nFound {len(filtered_urls)} URLs matching the pattern.")
        try:
            with open(output_csv_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['URL']) # Write header
                writer.writerows([[link] for link in filtered_urls])
            print(f"Successfully saved filtered URLs to '{output_csv_file}'")
        except Exception as e:
            print(f"Error writing output CSV '{output_csv_file}': {e}")
    else:
        print("\nNo URLs matched the specified verse pattern.")

# --- Function to Extract Verses to JSON ---
def extract_verses_to_json(input_csv_file, output_json_file):
    """
    Reads URLs from the filtered CSV, visits each URL, extracts headings and verses,
    and saves them to a JSON file.

    Args:
        input_csv_file (str): Path to the input CSV file (filtered URLs).
        output_json_file (str): Path to the output JSON file.
    """
    print(f"\n--- Step 3: Extracting Verses to JSON from '{input_csv_file}' --- ")
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

    # Load existing data from JSON file if it exists, to simulate appending
    all_verses_data = []
    try:
        with open(output_json_file, 'r', encoding='utf-8') as f_json:
            all_verses_data = json.load(f_json)
            if not isinstance(all_verses_data, list):
                print(f"Warning: Existing content in {output_json_file} is not a list. Starting fresh.")
                all_verses_data = []
            else:
                 print(f"Loaded {len(all_verses_data)} existing entries from {output_json_file}.")
    except FileNotFoundError:
        print(f"Output file '{output_json_file}' not found. Creating a new one.")
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {output_json_file}. Starting fresh.")
        all_verses_data = []
    except Exception as e:
        print(f"Error reading existing JSON file '{output_json_file}': {e}. Starting fresh.")
        all_verses_data = []

    verse_pattern = re.compile(r'॥\s*(\d+)\s*॥')

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

        processed_count = 0
        for i, url in enumerate(urls_to_process):
            print(f"Processing URL {i+1}/{len(urls_to_process)}: {url}")
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Extract Heading (h2 > h1 > title)
                heading_tag = soup.find('h2') or soup.find('h1') or soup.title
                heading = heading_tag.get_text(strip=True) if heading_tag else "Unknown Heading"
                heading = ' '.join(heading.split()) # Normalize whitespace

                # Extract body text
                body_tag = soup.body
                if not body_tag:
                    print("  [Warning: No body tag found]")
                    continue
                body_text = body_tag.get_text(separator='\n', strip=True)

                # Find verses using the marker pattern
                matches = list(verse_pattern.finditer(body_text))
                if not matches:
                    print("  [No verse markers found in body text]")
                    continue

                page_verses = []
                start_index = 0
                for match in matches:
                    verse_number = match.group(1)
                    end_index = match.start()
                    
                    # Extract text between previous marker and current one
                    raw_verse_text = body_text[start_index:end_index]
                    
                    # Basic cleaning: split lines, strip, keep non-empty
                    cleaned_verse_lines = [line.strip() for line in raw_verse_text.split('\n') if line.strip()]
                    verse_text = '\n'.join(cleaned_verse_lines)
                    
                    # Update start_index for the next iteration
                    start_index = match.end()

                    if verse_text: # Only add if there's cleaned text
                        ref = f"{heading}.{verse_number}"
                        verse_data = {"ref": ref, "verse": verse_text}
                        page_verses.append(verse_data)
                        print(f"    Found Verse: {ref}")
                    else:
                         print(f"    Verse {verse_number} marker found, but no text extracted before it.")
                
                all_verses_data.extend(page_verses)
                processed_count += 1
                time.sleep(0.5) # Shorter delay for potentially faster pages

            except TimeoutException:
                print(f"  [TIMEOUT processing {url}]")
            except Exception as e:
                print(f"  [ERROR processing {url}: {type(e).__name__} - {e}]")
                continue

    except Exception as e:
        print(f"An critical error occurred during the verse extraction process: {e}")
    finally:
        if driver:
            print("Closing WebDriver...")
            driver.quit()

    # Write the complete data to the JSON file
    if all_verses_data:
        print(f"\nProcessed {processed_count} URLs successfully.")
        print(f"Total verses extracted (including previous runs if any): {len(all_verses_data)}.")
        try:
            with open(output_json_file, 'w', encoding='utf-8') as outfile:
                json.dump(all_verses_data, outfile, ensure_ascii=False, indent=2)
            print(f"Successfully saved verses data to '{output_json_file}'")
        except Exception as e:
            print(f"Error writing final JSON to '{output_json_file}': {e}")
    else:
        print("\nNo verses were extracted in this run.")

# --- Main Execution ---
if __name__ == "__main__":
    target_url = "https://sanskritdocuments.org/doc_shiva/"
    initial_output_file = "shiva_document_links.csv"
    filtered_output_file = "filtered_url.csv"
    final_json_output = "output.json" # Define JSON filename
    
    # --- Step 1: Scraping --- #
    print("--- Step 1: Scraping initial links ---")
    print("Starting scraping process...")
    print("Requires: selenium, beautifulsoup4, requests")
    print("Requires: WebDriver (e.g., chromedriver) installed and in PATH.")
    scrape_shiva_links(target_url, initial_output_file)
    print("Scraping process finished.")

    # --- Step 2: Filtering --- #
    print("\n--- Step 2: Filtering links by verse pattern --- ")
    filter_urls_by_verse_pattern(initial_output_file, filtered_output_file)
    print("Filtering process finished.")

    # --- Step 3: Verse Extraction --- #
    extract_verses_to_json(filtered_output_file, final_json_output)
    print("\nVerse extraction process finished.")
