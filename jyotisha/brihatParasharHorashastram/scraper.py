import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Tuple
import re
import json
from datetime import datetime
import os

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

def scrape_webpage(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def extract_adhyaya_info(text: str) -> tuple:
    """Extract adhyaya number and title."""
    pattern = r'(.+?)॥\s*([\d१२३४५६७८९०]+)\s*॥'
    match = re.search(pattern, text)
    if match:
        title = match.group(1).strip()
        number = devanagari_to_english(match.group(2))
        return title, number
    return None, None

def extract_verses_page1(soup: BeautifulSoup) -> list:
    """Extract verses from the first page pattern."""
    verses = []
    
    # Print raw HTML structure
    print("\nRaw HTML structure:")
    print(soup.prettify()[:500])  # Print first 500 chars
    
    # Get text content
    content = soup.get_text('\n', strip=True)
    print("\nFirst 500 chars of content:")
    print(content[:500])
    
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    print(f"\nFound {len(lines)} lines")
    print("First 5 lines:")
    for line in lines[:5]:
        print(f"LINE: {line}")
    
    current_adhyaya = None
    current_adhyaya_title = None
    verse_buffer = []
    
    for line in lines:
        # Skip metadata and empty lines
        if any(skip in line for skip in ['Encoded and proofread by', 'Proofread by', '% Text title', 'doc_z_misc']):
            continue
            
        # Check for adhyaya header
        adhyaya_match = re.search(r'अथ\s*(.+?)अध्यायः\s*॥\s*([\d१२३४५६७८९०]+)\s*॥', line)
        if adhyaya_match:
            current_adhyaya_title = adhyaya_match.group(0)
            current_adhyaya = devanagari_to_english(adhyaya_match.group(2))
            print(f"\nFound adhyaya: {current_adhyaya_title} ({current_adhyaya})")
            continue
        
        # Check if line contains verse number
        verse_match = re.search(r'॥\s*([\d१२३४५६७८९०]+)\s*॥\s*$', line)
        if verse_match:
            verse_number = devanagari_to_english(verse_match.group(1))
            print(f"\nFound verse number: {verse_number}")
            
            # Clean the current line by removing the verse number
            clean_line = re.sub(r'॥\s*[\d१२३४५६७८९०]+\s*॥\s*$', '', line).strip()
            
            # If we have a previous line in buffer, combine them
            if verse_buffer:
                complete_verse = verse_buffer[0] + '\n' + clean_line
                print(f"Complete verse:\n{complete_verse}")
                
                # Add the verse with its reference
                if current_adhyaya:
                    verse_entry = {
                        'ref': f'बृहत्पाराशरहोराशास्त्रम्->{current_adhyaya}.{verse_number}',
                        'verse': complete_verse,
                        'metadata': {
                            'adhyaya_number': current_adhyaya,
                            'adhyaya_title': current_adhyaya_title
                        }
                    }
                    verses.append(verse_entry)
                    print(f"Added verse {current_adhyaya}.{verse_number}")
                verse_buffer = []
            else:
                verse_buffer = [clean_line]
                print(f"Started new verse with: {clean_line}")
        else:
            # If no verse number and buffer is empty, this might be first line of verse
            if not verse_buffer:
                verse_buffer = [line]
                print(f"Buffered line: {line}")
    
    print(f"\nFound {len(verses)} verses")
    return verses

def extract_verses(url, html_content):
    if not html_content:
        return []
        
    verses = []
    base_adhyaya_from_url = 0
    try:
        filename = url.split('/')[-1]
        match = re.search(r'par(\d{2})', filename) # Expecting 2 digits like 01, 11, 21 etc.
        if match:
            base_adhyaya_from_url = int(match.group(1))
            print(f"Extracted base Adhyaya from URL ({filename}): {base_adhyaya_from_url}")
        else:
             print(f"Could not extract base Adhyaya number from URL filename: {filename}")
    except Exception as e:
        print(f"Error extracting Adhyaya from URL: {e}")

    current_adhyaya = base_adhyaya_from_url # Initialize with URL base
    current_adhyaya_title = "Unknown Adhyaya" # Default title
    verse_buffer = []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    # Try to find a main content area if possible, otherwise use whole text
    # This might need adjustment based on actual page structure
    content_area = soup.find('pre') or soup.find('body') or soup 
    text = content_area.get_text('\n', strip=True)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Debug: Print first few lines to check content extraction
    print("--- Start of Text Processing ---")
    for i, line in enumerate(lines[:10]):
        print(f"Line {i}: {line}")
    print("------------------------------")

    # Initialize tracking variables for Adhyaya verse counts
    last_adhyaya_title = None
    last_adhyaya_number = 0
    last_adhyaya_verse_count = 0
    verse_count_in_adhyaya = 0 # Counter specific to the current adhyaya
    found_adhyaya_in_run = False # Flag if any adhyaya is found in this run
    adhyaya_number_tracker = set() # Track adhyaya numbers found in this run

    for i, line in enumerate(lines):
        # Skip metadata common in these documents
        if any(skip in line for skip in ['Encoded and proofread by', 'Proofread by', '% Text title', 'doc_z_misc', 'Document Information', 'Source:', 'Send corrections to', 'Last updated on', 'Site access', 'https://sanskritdocuments.org']):
            continue

        # Check for adhyaya header using a more flexible regex
        # Pattern: (Optional अथ) TitleEndingWithध्यायः [॥ or whitespace] Number [Optional ॥ or whitespace]
        # Example: सृष्टिक्रमकथनाध्यायः ॥ १॥ or अथ दशाफलाद्यायः ॥ ४७॥
        # NOTE: Corrected regex escaping for edit tool
        adhyaya_match = re.match(r'^\s*(?:अथ\s*)?(.+?ध्यायः)\s*[॥|\s]+\s*([\d१२३४५६७८९०]+)\s*[॥|\s]*\s*$', line)
        if adhyaya_match:
            new_adhyaya_title = adhyaya_match.group(1).strip()
            adhyaya_num_str = adhyaya_match.group(2)
            try:
                new_adhyaya_number = int(devanagari_to_english(adhyaya_num_str))

                # Finalize count for the *previous* adhyaya if it existed and had verses
                if last_adhyaya_title and last_adhyaya_verse_count > 0:
                    print(f"  -> Adhyaya {last_adhyaya_title} ({last_adhyaya_number}) finished with {last_adhyaya_verse_count} verses.")

                print(f"\n>>> Found Adhyaya: {new_adhyaya_title} (Number: {new_adhyaya_number})")

                # Update current adhyaya info *immediately*
                current_adhyaya_title = new_adhyaya_title
                current_adhyaya = new_adhyaya_number

                # Update tracking for the *new* adhyaya
                last_adhyaya_title = current_adhyaya_title
                last_adhyaya_number = current_adhyaya
                last_adhyaya_verse_count = 0 # Reset verse count for the new adhyaya
                found_adhyaya_in_run = True
                adhyaya_number_tracker.add(current_adhyaya) # Track found number

                verse_buffer = [] # Clear buffer for new adhyaya
                verse_count_in_adhyaya = 0 # Reset verse counter

            except ValueError:
                print(f"Error parsing Adhyaya number: {adhyaya_num_str}")
            continue # Move to the next line after finding an adhyaya title

        # Check if line contains verse number marker (end of a verse)
        verse_end_match = re.search(r'(.*?)॥\s*([\d१२३४५६७८९०]+)\s*॥\s*$', line)
        if verse_end_match:
            verse_content_part = verse_end_match.group(1).strip()
            verse_number_str = verse_end_match.group(2)
            verse_number = int(devanagari_to_english(verse_number_str))
            verse_count_in_adhyaya = verse_number # Use the number from the text as the count

            # Combine buffer with the current line's content part
            if verse_buffer:
                 # Add the last part of the verse (before the number)
                verse_buffer.append(verse_content_part)
                complete_verse = '\n'.join(verse_buffer).strip()
            else:
                 # Verse is a single line
                 complete_verse = verse_content_part

            if complete_verse and current_adhyaya_title != "Unknown Adhyaya": # Ensure we have a valid adhyaya context
                 verse_ref = f'बृहत्पाराशरहोराशास्त्रम्->{current_adhyaya}.{verse_number}'
                 # Check if this verse reference already exists in the list for this run
                 if any(v['ref'] == verse_ref for v in verses):
                      print(f"  -> Skipping duplicate verse detected during run: {verse_ref}")
                 else:
                      verse_entry = {
                        'ref': verse_ref,
                        'verse': complete_verse,
                        'metadata': {
                            'adhyaya_number': current_adhyaya,
                            'adhyaya_title': current_adhyaya_title
                        }
                      }
                      verses.append(verse_entry)
                      print(f"  -> Stored Verse: {current_adhyaya}.{verse_number} | Title: {current_adhyaya_title[:20]}...")
                      # Update the verse count for the *current* adhyaya
                      last_adhyaya_verse_count = verse_number
                      verse_count_in_adhyaya = verse_number
                      # print(f"     Verse Text:\\n{complete_verse}\\n-----") # Uncomment for full verse text debug

            verse_buffer = [] # Clear buffer after storing verse
        
        # If it's not an adhyaya line or end of verse, buffer it (part of a verse)
        elif line: # Avoid adding empty lines to buffer
            # Special handling for introductory lines like श्रीगणेशाय नमः ॥
            if line == 'श्रीगणेशाय नमः ॥' or line == '॥  ॐ ॥':
                 print(f"Skipping introductory line: {line}")
                 continue # Skip these specific lines
            verse_buffer.append(line)
            
    # Finalize count for the very last adhyaya processed in the file
    if last_adhyaya_title and last_adhyaya_verse_count > 0:
        print(f"  -> Adhyaya {last_adhyaya_title} ({last_adhyaya_number}) finished with {last_adhyaya_verse_count} verses.")

    print(f"--- End of Text Processing ({len(verses)} verses found) ---")
    return verses

def save_to_json(new_verses: List[Dict[str, str]], filename: str) -> None:
    """
    Save the scraped data to a JSON file, appending if the file exists.
    
    Args:
        new_verses (List[Dict[str, str]]): List of new verses to save
        filename (str): Output filename
    """
    existing_data = []
    try:
        # Check if file exists and is not empty
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                         print(f"Warning: Existing data in {filename} is not a list. Overwriting.")
                         existing_data = []
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filename}. Overwriting.")
                    existing_data = []
    except Exception as e:
        print(f"Error reading existing file {filename}: {e}. Starting fresh.")
        existing_data = [] # Ensure it's a list even if read fails

    # Append new verses
    existing_data.extend(new_verses)

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print(f"Data successfully appended to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def main():
    # Start with the first URL
    urls = [
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par0110.html", # Adhyayas 1-10
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par1120.html", # Adhyayas 11-20
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par2130.html", # Adhyayas 21-30 (with deduplication)
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.html", # Adhyayas 31-40
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par4145.html", # Adhyayas 41-45
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par4650.html", # Skipped for now (issues with 46/47)
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par5160.html", # Adhyayas 51-60
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par6170.html", # Adhyayas 61-70
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par7180.html", # Adhyayas 71-80
        # "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par8190.html", # Adhyayas 81-90
        "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par9197.html", # Adhyayas 91-97
    ]
    
    output_filename = 'output.json'
    # Optional: Clear the output file before starting the first run
    # if os.path.exists(output_filename):
    #    os.remove(output_filename)
    #    print(f"Cleared existing {output_filename}")

    # Process the first URL for now
    if urls:
        url = urls[0]
        try:
            print(f"\nProcessing URL: {url}")
            html_content = scrape_webpage(url)
            if html_content:
                 extracted_verses = extract_verses(url, html_content)
                 if extracted_verses:
                    save_to_json(extracted_verses, output_filename)
                    print(f"Extracted and appended {len(extracted_verses)} verses from {url}")
                 else:
                    print(f"No verses extracted from {url}")
            else:
                 print(f"Could not fetch content for {url}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    else:
        print("No URLs specified.")


if __name__ == "__main__":
     # Import os module needed for save_to_json
    main() 