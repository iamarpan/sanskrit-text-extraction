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
        # Handle cases where conversion might fail unexpectedly
        print(f"Warning: Could not convert Sanskrit numeral string '{num_str}' to integer.")
        raise # Re-raise to be caught later

# Helper function to convert Sanskrit ordinals to English numbers
def sanskrit_ordinal_to_english(ord_str):
    ordinal_map = {
        "प्रथमो": 1, "द्वितीयो": 2, "तृतीयो": 3, "चतुर्थो": 4, "पञ्चमो": 5,
        "षष्ठो": 6, "षष्टो": 6, # Added variation for Ch 6
        "सप्तमो": 7, "अष्टमो": 8, "नवमो": 9, "दशमो": 10,
        "एकादशो": 11, "एकादशमो": 11, # Added variation for Ch 11
        "द्वादशो": 12, "त्रयोदशो": 13, "चतुर्दशो": 14, "पञ्चदशो": 15,
        "षोडशो": 16, "सप्तदशो": 17, "अष्टादशो": 18, "एकोनविंशो": 19, "विंशो": 20,
        "एकविंशो": 21, "द्वाविंशो": 22, "त्रयोविंशो": 23, "चतुर्विंशो": 24, "पञ्चविंशो": 25, "पंचविंशो": 25, # Added variation for Ch 25
        "षड्विंशो": 26, "सप्तविंशो": 27, "अष्टाविंशो": 28
    }
    # Extract the base ordinal word
    for key in ordinal_map:
        if key in ord_str:
            return ordinal_map[key]
    print(f"Warning: Unknown Sanskrit ordinal '{ord_str}' encountered.")
    return None # Return None if no match found

# URL of the document
url = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/phaladIpika.html"

# Target output file in the current directory
output_file = "output.json"

# Define a User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch HTML content
print(f"Fetching content from {url}...")
try:
    # Add the headers parameter to the get request
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Raise HTTPError for bad responses
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
current_adhyaya_number = 1 # Start with Chapter 1 as default
current_adhyaya_name = "प्रथमोऽध्यायः" # Default name until first heading is parsed
verse_buffer = []
# Updated Adhyaya heading pattern (removed ##)
adhyaya_heading_pattern = re.compile(r"^\s*(.*?ऽध्यायः)\s*$")
# Pattern to find verse number at the end of a line
verse_end_pattern = re.compile(r"(.*)(॥\s*([०-९]+)\s*॥)\s*$", re.DOTALL)

# Remove start/end marker logic - process all lines from <pre>
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
            current_adhyaya_name = new_adhyaya_name # Update name only if number is valid
            # Clear buffer when a new chapter starts
            if verse_buffer:
                 print(f"Warning: Clearing non-empty buffer at chapter change ({new_adhyaya_name}). Content: {' '.join(verse_buffer)}")
            verse_buffer = []
        else:
            print(f"Warning: Could not determine chapter number for heading: {new_adhyaya_name}")
            # Keep previous chapter context but clear buffer? Or stop? Let's clear buffer.
            verse_buffer = []
        continue # Skip processing the heading line as verse content

    # Skip empty lines
    if not stripped_line:
        continue

    # Accumulate verse lines. Use original line to preserve potential leading whitespace/formatting
    verse_buffer.append(line)

    # Check if the *stripped* line ends with the verse number pattern
    # We check stripped_line but reconstruct using the buffer later
    verse_match = verse_end_pattern.search(stripped_line)
    if verse_match:
        sanskrit_verse_num_str = verse_match.group(3)
        try:
            verse_number = sanskrit_numeral_to_english(sanskrit_verse_num_str)

            # Reconstruct verse text from buffer
            full_verse_text_from_buffer = "\n".join(verse_buffer)

            # Remove the verse number ending from the reconstructed text
            # Apply regex to the full buffer content in case verse number is on its own line
            final_match = verse_end_pattern.search(full_verse_text_from_buffer)
            if final_match:
                 cleaned_verse_text = final_match.group(1).strip()
            else:
                 # Fallback if pattern doesn't match buffer end (shouldn't happen often)
                 cleaned_verse_text = verse_end_pattern.sub('', full_verse_text_from_buffer).strip()


            if cleaned_verse_text: # Ensure we don't add empty verses
                verse_entry = {
                    "verse": cleaned_verse_text,
                    "ref": f"फलदीपिका->{current_adhyaya_number}.{verse_number}",
                    "metadata": {
                        "adhyaya_name": current_adhyaya_name
                    }
                }
                verses_data.append(verse_entry)
                # print(f"  Added verse: {current_adhyaya_number}.{verse_number}") # Debugging output

            # Clear buffer for the next verse
            verse_buffer = []

        except ValueError:
            # Error already printed by helper function
            print(f"Skipping verse due to numeral conversion error near line: {stripped_line}")
            verse_buffer = [] # Clear buffer on error
        except Exception as e:
             print(f"An unexpected error occurred processing verse near line '{stripped_line}': {e}")
             verse_buffer = [] # Clear buffer on error


# Handle any remaining content in the buffer after the loop
if verse_buffer:
    print(f"Warning: Trailing content found in buffer after loop: {' '.join(verse_buffer)}")

# Write the data to JSON file
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