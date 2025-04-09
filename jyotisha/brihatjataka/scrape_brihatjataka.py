import requests
from bs4 import BeautifulSoup
import re
import json
import os

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

# Helper function to convert Sanskrit ordinals to English numbers
def sanskrit_ordinal_to_english(ord_str):
    # Updated map from previous run, might need adjustments for this text
    ordinal_map = {
        "प्रथमो": 1, "द्वितीयो": 2, "तृतीयो": 3, "चतुर्थो": 4, "पञ्चमो": 5,
        "षष्ठो": 6, "षष्टो": 6,
        "सप्तमो": 7, "अष्टमो": 8, "नवमो": 9, "दशमो": 10,
        "एकादशो": 11, "एकादशमो": 11,
        "द्वादशो": 12, "त्रयोदशो": 13, "चतुर्दशो": 14, "पञ्चदशो": 15,
        "षोडशो": 16, "सप्तदशो": 17, "अष्टादशो": 18, "एकोनविंशो": 19, "विंशो": 20,
        "एकविंशो": 21, "द्वाविंशो": 22, "त्रयोविंशो": 23, "चतुर्विंशो": 24,
        "पञ्चविंशो": 25, "पंचविंशो": 25,
        "षड्विंशो": 26, "सप्तविंशो": 27, "अष्टाविंशो": 28
        # Add more if needed for Brihat Jataka (up to 28 based on ToC)
    }
    for key in ordinal_map:
        if key in ord_str:
            return ordinal_map[key]
    print(f"Warning: Unknown Sanskrit ordinal '{ord_str}' encountered.")
    return None

# URL of the document
url = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/brihajjAtakam.html"
book_name = "बृहज्जातक"
# Target output file
output_file = "brihatjataka_output.json"

# Define a User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch HTML content
print(f"Fetching content from {url}...")
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print("Content fetched successfully.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL {url}: {e}")
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
current_adhyaya_number = 1 # Default to 1
current_adhyaya_name = "Unknown Adhyaya" # Default name
verse_buffer = []
adhyaya_heading_pattern = re.compile(r"^\s*(.*?ऽध्यायः)\s*$")
verse_end_pattern = re.compile(r"(.*)(॥\s*([०-९]+)\s*॥)\s*$", re.DOTALL)

for line in lines:
    stripped_line = line.strip()

    # Check for Adhyaya heading first
    adhyaya_match = adhyaya_heading_pattern.match(stripped_line)
    if adhyaya_match:
        new_adhyaya_name = adhyaya_match.group(1).strip()
        print(f"Found Adhyaya heading: {new_adhyaya_name}")
        ordinal_part = new_adhyaya_name.split('ऽ')[0]
        num = sanskrit_ordinal_to_english(ordinal_part)
        if num is not None:
            current_adhyaya_number = num
            current_adhyaya_name = new_adhyaya_name
            if verse_buffer:
                print(f"Warning: Clearing non-empty buffer at chapter change ({new_adhyaya_name}). Content: {' '.join(verse_buffer)}")
            verse_buffer = []
        else:
            print(f"Warning: Could not determine chapter number for heading: {new_adhyaya_name}")
            # Keep previous chapter context but update name if possible?
            # Let's update the name but keep the number for now, and clear buffer.
            current_adhyaya_name = new_adhyaya_name
            verse_buffer = []
        continue

    if not stripped_line:
        continue

    verse_buffer.append(line)

    verse_match = verse_end_pattern.search(stripped_line)
    if verse_match:
        sanskrit_verse_num_str = verse_match.group(3)
        try:
            verse_number = sanskrit_numeral_to_english(sanskrit_verse_num_str)
            full_verse_text_from_buffer = "\n".join(verse_buffer)
            final_match = verse_end_pattern.search(full_verse_text_from_buffer)
            if final_match:
                 cleaned_verse_text = final_match.group(1).strip()
            else:
                 cleaned_verse_text = verse_end_pattern.sub('', full_verse_text_from_buffer).strip()

            if cleaned_verse_text:
                verse_entry = {
                    "verse": cleaned_verse_text,
                    "ref": f"{book_name}->{current_adhyaya_number}.{verse_number}",
                    "metadata": {
                        "adhyaya_name": current_adhyaya_name
                    }
                }
                verses_data.append(verse_entry)

            verse_buffer = []

        except ValueError:
            print(f"Skipping verse due to numeral conversion error near line: {stripped_line}")
            verse_buffer = []
        except Exception as e:
             print(f"An unexpected error occurred processing verse near line '{stripped_line}': {e}")
             verse_buffer = []

if verse_buffer:
    # Check if the remaining buffer looks like the start of the table of contents
    buffer_content = "\n".join(verse_buffer).strip()
    if not buffer_content.startswith("01. rAzi prabheda"):
        print(f"Warning: Trailing content found in buffer after loop: {buffer_content[:200]}...") # Print start of buffer


print(f"Writing {len(verses_data)} extracted verses to {output_file}...")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verses_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully scraped data and saved to {output_file}")
except IOError as e:
    print(f"Error writing to file {output_file}: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during file writing: {e}")
    exit(1)

print("Script finished.") 