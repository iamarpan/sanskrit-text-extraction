import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import re
import json
from datetime import datetime

def scrape_webpage(url: str) -> Optional[BeautifulSoup]:
    """
    Scrape a webpage and return its parsed content.
    
    Args:
        url (str): The URL of the webpage to scrape
        
    Returns:
        Optional[BeautifulSoup]: Parsed HTML content if successful, None otherwise
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Send GET request to the URL with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'lxml')
        return soup
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage {url}: {e}")
        return None

def extract_verses(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Extract verses from the Amba Navamanimala webpage.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        List[Dict[str, str]]: List of verses with their numbers and content
    """
    verses = []
    
    # Find the pre tag with id="content"
    content = soup.find('pre', id='content')
    if not content:
        print("Could not find content tag")
        return verses
        
    # Remove the h2 tag with itemprop="name" if it exists
    h2_tag = content.find('h2', attrs={'itemprop': 'name'})
    if h2_tag:
        h2_tag.decompose()
        
    # Get text content
    text_content = content.get_text()
    
    # Find all text that matches the verse pattern (e.g., "॥ १॥")
    verse_pattern = re.compile(r'॥\s*(\d+)\s*॥')
    
    # Split text by verse endings
    verse_parts = verse_pattern.split(text_content)
    
    # Process verse parts
    for i in range(0, len(verse_parts)-1, 2):
        verse_text = verse_parts[i].strip()
        verse_number = verse_parts[i+1]
        
        # Skip if no verse number or text
        if not verse_number or not verse_text:
            continue
            
        # For the first verse, clean up any header text
        if i == 0:
            # Find the first occurrence of actual verse text
            lines = verse_text.split('\n')
            for j, line in enumerate(lines):
                if any(char.isalpha() for char in line):
                    verse_text = '\n'.join(lines[j:])
                    break
        
        verses.append({
            'verse_number': verse_number,
            'text': verse_text.strip()
        })
    
    return verses

def load_existing_verses(filename: str) -> List[Dict[str, str]]:
    """
    Load existing verses from the output.json file.
    
    Args:
        filename (str): Path to the output.json file
        
    Returns:
        List[Dict[str, str]]: List of existing verses
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(verses: List[Dict[str, str]], filename: str) -> None:
    """
    Save the scraped data to a JSON file.
    
    Args:
        verses (List[Dict[str, str]]): List of verses to save
        filename (str): Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(verses, f, ensure_ascii=False, indent=2)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def convert_devanagari_to_english(number: str) -> str:
    """
    Convert Devanagari numbers to English numbers.
    
    Args:
        number (str): Devanagari number string (e.g., "४-१")
        
    Returns:
        str: English number string (e.g., "4-1")
    """
    devanagari_to_english = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    return ''.join(devanagari_to_english.get(c, c) for c in number)

def process_url(url: str) -> List[Dict[str, str]]:
    """
    Process a single URL and return formatted verses.
    
    Args:
        url (str): URL to process
        
    Returns:
        List[Dict[str, str]]: List of formatted verses
    """
    soup = scrape_webpage(url)
    if not soup:
        return []
        
    verses = extract_verses(soup)
    formatted_verses = []
    
    for verse in verses:
        verse_number = verse['verse_number']
        english_number = convert_devanagari_to_english(verse_number)
        ref = f'अम्बा नवमणिमाला->{english_number}'
        formatted_verses.append({
            'ref': ref,
            'verse': verse['text']
        })
    
    return formatted_verses

def main():
    # URL for Amba Navamanimala
    url = "https://sanskritdocuments.org/doc_devii/ambAnavamaNimAlA.html"
    
    # Load existing verses
    existing_verses = load_existing_verses('output.json')
    all_verses = existing_verses.copy()
    
    # Process the URL
    print(f"\nProcessing URL: {url}")
    formatted_verses = process_url(url)
    all_verses.extend(formatted_verses)
    
    # Print example verses
    print("\nExample verses:")
    print("-" * 80)
    for verse in formatted_verses[:3]:
        print(f"Reference: {verse['ref']}")
        print(verse['verse'])
        print("-" * 80)
    
    # Save all verses to output.json
    save_to_json(all_verses, 'output.json')
    print(f"\nTotal verses in output.json: {len(all_verses)}")

if __name__ == "__main__":
    main() 
