import requests
from bs4 import BeautifulSoup
import re
import json
import os

# Configuration
URL = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/laghujAtaka.html"
OUTPUT_FILE = "laghujatakam_output.json"
BOOK_NAME = "Laghujatakam" # For use in references

# --- Helper Functions ---
# (No numeral conversion needed as numbers seem Arabic)

# --- Main Scraping Logic ---
def scrape_laghujatakam(url, output_file):
    print(f"Fetching content from {url}...")
    # Add standard browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers) # Add headers here
        response.raise_for_status()  # Raise an exception for bad status codes
        response.encoding = 'utf-8' # Ensure correct encoding
        html_content = response.text
        print("Content fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        exit(1)

    print("Parsing HTML content...")
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- Find the main content ---
    # This is an educated guess. Sanskritdocuments.org often wraps main content.
    # We might need to adjust this based on the actual HTML structure.
    # Let's try finding a common container or just use the body text for now.
    content_area = soup.body
    if not content_area:
        print("Error: Could not find the main content area (body tag).")
        exit(1)

    # Get text, preserving line breaks somewhat by joining paragraphs/blocks
    text_content = '\n'.join(p.get_text() for p in content_area.find_all(['p', 'div', 'pre']))
    if not text_content:
         # Fallback if specific tags don't work, get all body text
         print("Warning: Could not extract text from specific tags, using full body text.")
         text_content = content_area.get_text(separator='\n', strip=True)

    if not text_content:
         print("Error: Failed to extract any text content.")
         exit(1)

    print("Extracted text content. Processing...")

    # --- Regex Patterns ---
    # Chapter heading: Captures name (group 1) and Arabic number (group 2)
    chapter_pattern = re.compile(r"^\s*अथ\s+(.*?ध्यायः)\s*॥\s*(\d+)\s*॥")
    # Verse ending: Captures text (group 1), separator (group 2), Arabic number (group 3)
    # Uses DOTALL to match across newlines if needed, non-greedy text capture.
    # Simplified to only match the ॥ number ॥ format.
    verse_pattern = re.compile(r"(.*?)(॥\s*)(\d+)\s*॥\s*$", re.DOTALL)

    # --- Data Storage ---
    verses_data = []
    current_chapter_name = "Unknown Chapter"
    current_chapter_num = 0
    verse_buffer = []
    skipping_header = True # Skip intro/TOC before first chapter

    # --- Processing Loop ---
    lines = text_content.splitlines()
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if not stripped_line:
            continue # Skip empty lines

        # Check for Chapter Heading
        chapter_match = chapter_pattern.match(stripped_line)
        if chapter_match:
            current_chapter_name = chapter_match.group(1).strip()
            current_chapter_num = int(chapter_match.group(2))
            print(f"Found Chapter {current_chapter_num}: '{current_chapter_name}'")
            verse_buffer = [] # Reset buffer for new chapter
            skipping_header = False # Start processing verses
            continue

        # Skip lines until the first chapter heading is found
        if skipping_header:
            continue

        # Add non-empty lines to buffer
        verse_buffer.append(line) # Keep original spacing within verse

        # Check for Verse ending at the end of the *buffered content*
        # Join buffer to check potentially multi-line verses
        buffered_text = "\n".join(verse_buffer)
        verse_match = verse_pattern.search(buffered_text)

        if verse_match:
            # Extract verse text (group 1) and number (group 3)
            verse_text = verse_match.group(1).strip()
            sutra_number_str = verse_match.group(3)

            try:
                sutra_number = int(sutra_number_str)

                if current_chapter_num > 0 and verse_text: # Ensure we are inside a chapter
                    ref = f"{BOOK_NAME}->{current_chapter_num}.{sutra_number}"
                    verse_entry = {
                        "verse": verse_text,
                        "ref": ref,
                        "metadata": {
                            "chapter_name": current_chapter_name,
                            "chapter_number": current_chapter_num,
                            "verse_number": sutra_number
                        }
                    }
                    verses_data.append(verse_entry)
                    # print(f"  Extracted verse: {ref}")

                verse_buffer = [] # Clear buffer after processing verse

            except ValueError:
                print(f"Warning: Could not convert verse number '{sutra_number_str}' to int near line {line_num}: {stripped_line}")
                # Decide whether to clear buffer or keep accumulating
                # verse_buffer = [] # Clear buffer on error for safety
            except Exception as e:
                 print(f"An unexpected error occurred processing verse near line {line_num} '{stripped_line}': {e}")
                 verse_buffer = [] # Clear buffer on error

    # --- Final Output ---
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

# --- Run the Scraper ---
if __name__ == "__main__":
    scrape_laghujatakam(URL, OUTPUT_FILE) 