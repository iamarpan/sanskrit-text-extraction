import requests
from bs4 import BeautifulSoup
import re
import json
import os

# Configuration
URL = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/bRRihatsaMhitA.html"
OUTPUT_FILE = "output.json" # Output within its own directory
# Use Devanagari script for the book name in references
BOOK_NAME = "बृहत्संहिता"

# Helper function to convert Sanskrit numerals (Devanagari) to English numerals
def sanskrit_numeral_to_english(num_str):
    sanskrit_digits = "०१२३४५६७८९"
    english_digits = "0123456789"
    trans_table = str.maketrans(sanskrit_digits, english_digits)
    try:
        return int(num_str.translate(trans_table))
    except ValueError:
        print(f"Warning: Could not convert Sanskrit numeral string '{num_str}' to integer.")
        raise

# Define a User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch HTML content
print(f"Fetching content from {URL}...")
try:
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    print("Content fetched successfully.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL {URL}: {e}")
    exit(1)

# Parse HTML
print("Parsing HTML content...")
soup = BeautifulSoup(response.content, 'html.parser')

# Find the <pre> tag
pre_tag = soup.find('pre')
if not pre_tag:
    print("Error: Could not find the <pre> tag containing the text.")
    exit(1)

# Extract text from the <pre> tag
pre_text = pre_tag.get_text(separator='\n')
lines = pre_text.splitlines()
print("Extracted text from <pre> tag.")

# Process lines to extract verses
print("Processing text to extract verses...")
verses_data = []
current_adhyaya_number = 0 # Default to 0 or handle case where first verse appears before first heading
current_adhyaya_name = "Unknown Adhyaya" # Default name
verse_buffer = []

# Updated pattern for chapter heading: <number> <name> (no ##)
adhyaya_heading_pattern = re.compile(r"^\s*([०-९]+)\s+(.*?ध्यायः)\s*$")
# Pattern for verse ending: ॥ X.YY ॥
verse_end_pattern = re.compile(r"(.*)(॥\s*([०-९]+\.[०-९]+)\s*॥)\s*$", re.DOTALL)
# Pattern to remove (K.<...>) annotations
k_annotation_pattern = re.compile(r'\(K\..*?\)')

for line in lines:
    stripped_line = line.strip()

    # Check for Adhyaya heading first
    adhyaya_match = adhyaya_heading_pattern.match(stripped_line)
    if adhyaya_match:
        sanskrit_num_str = adhyaya_match.group(1)
        new_adhyaya_name = adhyaya_match.group(2).strip()
        try:
            current_adhyaya_number = sanskrit_numeral_to_english(sanskrit_num_str)
            current_adhyaya_name = new_adhyaya_name
            print(f"Found Adhyaya: {current_adhyaya_number} - {current_adhyaya_name}")
            if verse_buffer:
                 print(f"Warning: Clearing non-empty buffer at chapter change ({current_adhyaya_name}). Content: {' '.join(verse_buffer)}")
            verse_buffer = []
        except ValueError:
            print(f"Warning: Could not determine chapter number for heading: {stripped_line}")
            # Update name but keep previous number? Or use placeholder?
            current_adhyaya_name = new_adhyaya_name # Keep name if possible
            verse_buffer = []
        continue

    if not stripped_line:
        continue

    verse_buffer.append(line)

    verse_match = verse_end_pattern.search(stripped_line)
    if verse_match:
        verse_ref_str = verse_match.group(3) # This is the X.YY string
        try:
            # Reconstruct verse text from buffer
            full_verse_text_from_buffer = "\n".join(verse_buffer)

            # Remove the verse number ending from the reconstructed text
            final_match = verse_end_pattern.search(full_verse_text_from_buffer)
            if final_match:
                 base_verse_text = final_match.group(1).strip()
            else:
                 base_verse_text = verse_end_pattern.sub('', full_verse_text_from_buffer).strip()

            # Clean the verse text
            cleaned_verse_text = k_annotation_pattern.sub('', base_verse_text)
            cleaned_verse_text = cleaned_verse_text.replace('*', ' ').strip()

            if cleaned_verse_text:
                verse_entry = {
                    "verse": cleaned_verse_text,
                    # Construct the full reference string
                    "ref": f"{BOOK_NAME}->{verse_ref_str}",
                    "metadata": {
                        "adhyaya_number": current_adhyaya_number,
                        "adhyaya_name": current_adhyaya_name
                    }
                }
                verses_data.append(verse_entry)

            verse_buffer = []

        except Exception as e:
             print(f"An unexpected error occurred processing verse ending with ref '{verse_ref_str}' near line '{stripped_line}': {e}")
             verse_buffer = []

# Handle trailing content (usually metadata/notes at the end)
if verse_buffer:
    buffer_content = "\n".join(verse_buffer).strip()
    # Check if it looks like the typical footer/notes
    if not buffer_content.startswith(("Originally digitized by", "% Text title", "इति श्रीवराहमिहिरकृतौ", "इति ब्रिहत्संहिता समाप्ता")):
        print(f"Warning: Trailing content found in buffer after loop: {buffer_content[:200]}...")


print(f"Writing {len(verses_data)} extracted verses to {OUTPUT_FILE}...")
try:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(verses_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully scraped data and saved to {OUTPUT_FILE}")
except IOError as e:
    print(f"Error writing to file {OUTPUT_FILE}: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during file writing: {e}")
    exit(1)

print("Script finished.") 