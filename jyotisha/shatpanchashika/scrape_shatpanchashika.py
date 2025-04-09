import requests
from bs4 import BeautifulSoup
import re
import json
import os

# Configuration
URL = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/ShaTpanchAshikA.html"
OUTPUT_FILE = "shatpanchashika_output.json"
# Use Devanagari script for the book name in references
BOOK_NAME = "षट्पञ्चाशिका"

# Hardcoded Chapter Names (based on TOC in the source)
# Mapping chapter number to name
CHAPTER_NAMES = {
    1: "अथ होराध्याय",
    2: "गमागमाध्यायः",
    3: "जयपराजयोऽध्यायः", # Note: Name might differ slightly from ending marker
    4: "शुभाशुभलक्षणाध्यायः",
    5: "प्रवासचिन्ताध्याय",
    6: "अथ नष्टप्राप्त्याध्याय",
    7: "अथ मिश्रकाध्याय"
}

# --- Main Scraping Logic ---
def scrape_shatpanchashika(url, output_file):
    print(f"Fetching content from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html_content = response.text
        print("Content fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        exit(1)

    print("Parsing HTML content...")
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract text content (similar strategy as before)
    content_area = soup.body
    if not content_area:
        print("Error: Could not find the main content area (body tag).")
        exit(1)
    text_content = '\n'.join(p.get_text() for p in content_area.find_all(['p', 'div', 'pre', 'h2', 'h3'])) # Added h2, h3
    if not text_content:
         print("Warning: Could not extract text from specific tags, using full body text.")
         text_content = content_area.get_text(separator='\n', strip=True)
    if not text_content:
         print("Error: Failed to extract any text content.")
         exit(1)

    print("Extracted text content. Processing...")

    # --- Regex Patterns ---
    # Verse ending: Captures text (group 1), separator (group 2), Arabic number (group 3)
    verse_pattern = re.compile(r"(.*?)(॥\s*)(\d+)\s*॥\s*$", re.DOTALL)
    # Chapter ending marker
    chapter_end_pattern = re.compile(r"^\s*इति श्री.*?ध्यायः.*?सम्पूर्णः\s*।")
    # Optional: Pattern to find the start of the first chapter to skip preamble
    first_chapter_start_pattern = re.compile(r"अथ होराध्याय")

    # --- Data Storage ---
    verses_data = []
    current_chapter_num = 0 # Start at 0, becomes 1 when first chapter starts
    verse_buffer = []
    processing_started = False # Flag to skip preamble

    # --- Processing Loop ---
    lines = text_content.splitlines()
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        # Check for start of processing (first chapter heading)
        if not processing_started:
            if first_chapter_start_pattern.search(stripped_line):
                print("Found start of Chapter 1.")
                processing_started = True
                current_chapter_num = 1 # Now we are in chapter 1
            else:
                continue # Skip preamble lines

        # Check for Chapter Ending *before* processing verse
        # This means the verse belongs to the chapter *before* this ending line
        if chapter_end_pattern.match(stripped_line):
            print(f"Found end of Chapter {current_chapter_num}.")
            # Increment chapter number for subsequent verses
            current_chapter_num += 1
            verse_buffer = [] # Clear buffer at chapter end
            continue

        # Add non-empty lines to buffer (only if processing has started)
        if processing_started:
             verse_buffer.append(line)

        # Check for Verse ending at the end of the buffered content
        buffered_text = "\n".join(verse_buffer)
        verse_match = verse_pattern.search(buffered_text)

        if verse_match:
            verse_text = verse_match.group(1).strip()
            sutra_number_str = verse_match.group(3)

            try:
                sutra_number = int(sutra_number_str)
                current_chapter_name = CHAPTER_NAMES.get(current_chapter_num, f"Unknown Chapter {current_chapter_num}")

                # Ensure we are inside a known chapter and have text
                if current_chapter_num > 0 and verse_text:
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
                    # print(f"  Extracted verse: {ref} (Chapter {current_chapter_num})")

                verse_buffer = [] # Clear buffer after processing verse

            except ValueError:
                print(f"Warning: Could not convert verse number '{sutra_number_str}' to int near line {line_num}: {stripped_line}")
                verse_buffer = [] # Clear buffer on error
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
    scrape_shatpanchashika(URL, OUTPUT_FILE) 