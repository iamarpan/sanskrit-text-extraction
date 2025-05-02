import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

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
                continue # Skip to the next URL

    except Exception as e:
        # Catch broader errors like WebDriver initialization failure
        print(f"A critical error occurred during the filtering process: {e}")
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

if __name__ == "__main__":
    input_csv_file = "shiva_document_links.csv"
    filtered_output_file = "filtered_urls.csv"
    
    print("--- Filtering links by verse pattern ---")
    filter_urls_by_verse_pattern(input_csv_file, filtered_output_file)
    print("Filtering process finished.") 