import csv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

# Define a common browser User-Agent
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
    
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Uncomment to run Chrome in the background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={headers['User-Agent']}")
    
    driver = None
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)

        # Wait for the list items with class 'devanagari' to be present
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

if __name__ == "__main__":
    target_url = "https://sanskritdocuments.org/doc_shiva/"
    initial_output_file = "shiva_document_links.csv"
    
    print("--- Scraping initial links ---")
    print("Starting scraping process...")
    print("Requires: selenium, beautifulsoup4")
    print("Requires: WebDriver (e.g., chromedriver) installed and in PATH.")
    scrape_shiva_links(target_url, initial_output_file)
    print("Scraping process finished.") 