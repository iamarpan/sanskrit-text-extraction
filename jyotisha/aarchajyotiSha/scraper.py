import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import re
import json
from datetime import datetime

def devanagari_to_english(number: str) -> str:
    """
    Convert Devanagari numerals to English numerals.
    
    Args:
        number (str): Number in Devanagari numerals
        
    Returns:
        str: Number in English numerals
    """
    devanagari_nums = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
                      '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
    
    return ''.join(devanagari_nums.get(char, char) for char in str(number))

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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send GET request to the URL with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage {url}: {e}")
        return None

def extract_verses(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Extract verses from the Archajyotisha webpage.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        List[Dict[str, str]]: List of verses with their numbers and content
    """
    verses = []
    
    # Find all pre tags (the content might be in a pre tag)
    content = soup.get_text()
    
    # Split content into lines and clean them
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Find the start of the actual verses (after the title)
    start_idx = 0
    for i, line in enumerate(lines):
        if 'पंचसंवत्सरमयं' in line:
            start_idx = i
            break
    
    # Process lines in pairs to extract verses
    i = start_idx
    while i < len(lines) - 1:
        line1 = lines[i]
        line2 = lines[i + 1] if i + 1 < len(lines) else ""
        
        # Check if this is a verse (second line ends with verse number)
        if '॥' in line2:
            # Extract verse number
            verse_match = re.search(r'॥\s*([\d१२३४५६७८९०]+)\s*॥', line2)
            if verse_match:
                verse_number = devanagari_to_english(verse_match.group(1))
                # Remove the verse number from the second line
                line2 = re.sub(r'॥\s*[\d१२३४५६७८९०]+\s*॥', '', line2).strip()
                verse_text = f"{line1}\n{line2}"
                
                verses.append({
                    'verse_number': verse_number,
                    'text': verse_text.strip()
                })
                i += 2  # Move to the next pair of lines
            else:
                i += 1
        else:
            i += 1
    
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
        ref = f'आर्चज्योतिषम्->{verse_number}'
        formatted_verses.append({
            'ref': ref,
            'verse': verse['text']
        })
    
    return formatted_verses

def main():
    base_url = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/aarchajyotiSha.html"
    all_verses = []
    
    formatted_verses = process_url(base_url)
    all_verses.extend(formatted_verses)
        
    # Print example verses from this URL
    print("\nExample verses from this URL:")
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