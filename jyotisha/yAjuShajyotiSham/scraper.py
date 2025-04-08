import requests
from bs4 import BeautifulSoup
import json
import re
import os

# Function to convert Devanagari numerals to English numerals
def devanagari_to_english(num_str):
    devanagari_nums = '०१२३४५६७८९'
    english_nums = '0123456789'
    trans_table = str.maketrans(devanagari_nums, english_nums)
    return num_str.translate(trans_table)

def extract_verses(url, html_content):
    if not html_content:
        return []

    verses = []
    text_title = "याजुषज्योतिषम्" # Use Devanagari title
    verse_buffer = []

    soup = BeautifulSoup(html_content, 'html.parser')
    content_area = soup.find('pre')
    if not content_area:
        print("Could not find <pre> tag containing the text.")
        return []

    text = content_area.get_text('\n', strip=False) # Keep original spacing for line breaks
    lines = text.split('\n') # Split by newline

    print(f"--- Start of Text Processing for {text_title} ---")
    line_count = 0
    verse_count = 0

    for i, line in enumerate(lines):
        line = line.strip() # Strip leading/trailing whitespace for processing
        if not line: # Skip empty lines
             continue

        line_count += 1
        # Skip metadata common in these documents
        if any(skip in line for skip in ['Encoded and proofread by', 'Proofread by', '% Text title', 'doc_z_misc', 'Document Information', 'Source:', 'Send corrections to', 'Last updated on', 'Site access', 'https://sanskritdocuments.org', 'BACK TO TOP', 'sanskritdocuments.org', 'Home sociology_astrology', 'ITX Devanagari PDF', 'PRINT']):
            # print(f"Skipping metadata/header line: {line}")
            continue
        # Skip specific title lines for this text
        if line == text_title or line == "याजुषज्योतिषम्" or line.startswith('॥ इति'):
            # print(f"Skipping title/footer line: {line}")
            continue

        # Check if line contains verse number marker (end of a verse)
        # Regex looks for potential verse text, then ॥, digits, ॥ at the end
        verse_end_match = re.search(r'(.*?)॥\s*([\d१२३४५६७८९०]+)\s*॥\s*$', line)
        if verse_end_match:
            verse_content_part = verse_end_match.group(1).strip()
            verse_number_str = verse_end_match.group(2)
            try:
                verse_number = int(devanagari_to_english(verse_number_str))
            except ValueError:
                print(f"Error parsing verse number: {verse_number_str} in line: {line}")
                verse_buffer.append(line) # Buffer the line if number parsing fails
                continue

            # Combine buffer with the current line's content part
            if verse_buffer:
                # Add the last part of the verse (before the number)
                if verse_content_part: # Add only if there's content before number
                    verse_buffer.append(verse_content_part)
                complete_verse = '\n'.join(verse_buffer).strip()
            else:
                # Verse is a single line
                complete_verse = verse_content_part

            if complete_verse: # Ensure we have verse text
                 verse_ref = f'{text_title}->{verse_number}'
                 verse_entry = {
                    'ref': verse_ref,
                    'verse': complete_verse
                 }
                 verses.append(verse_entry)
                 verse_count += 1
                 print(f"  -> Stored Verse: {verse_number}")
                 # print(f"     Verse Text:\n{complete_verse}\n-----") # Uncomment for full verse text debug

            verse_buffer = [] # Clear buffer after storing verse

        # If it's not an end-of-verse line, buffer it (part of a verse)
        elif line: # Avoid adding empty lines to buffer
            verse_buffer.append(line)

    # Check if anything is left in the buffer (maybe text without a proper verse ending)
    if verse_buffer:
        print(f"Warning: Content remaining in buffer (potential incomplete verse):")
        for buf_line in verse_buffer:
            print(f"  [Buffer] {buf_line}")


    print(f"--- End of Text Processing ({verse_count} verses found from {line_count} lines processed) ---")
    return verses

def main():
    url = "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/yaajuShajyotiSha.html"
    output_file = "output.json"
    all_verses = []

    # Load existing data if output file exists
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_verses = json.load(f)
            print(f"Loaded {len(all_verses)} verses from {output_file}")
        except json.JSONDecodeError:
            print(f"Error reading {output_file}. Starting fresh.")
            all_verses = []
        except Exception as e:
            print(f"An error occurred while loading {output_file}: {e}. Starting fresh.")
            all_verses = []

    existing_refs = {v['ref'] for v in all_verses}
    print(f"Processing URL: {url}")

    # Add a standard User-Agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        response.encoding = 'utf-8' # Ensure correct encoding
        html_content = response.text

        new_verses = extract_verses(url, html_content)

        added_count = 0
        for verse in new_verses:
            if verse['ref'] not in existing_refs:
                all_verses.append(verse)
                existing_refs.add(verse['ref'])
                added_count += 1

        if added_count > 0:
            # Sort verses based on the verse number within the ref
            def sort_key(verse_entry):
                try:
                    # Extract number part after '->'
                    num_part = verse_entry['ref'].split('->')[1]
                    return int(num_part)
                except (IndexError, ValueError):
                    return float('inf') # Put invalid refs at the end

            all_verses.sort(key=sort_key)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_verses, f, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to {output_file}. Added {added_count} new verses.")
            print(f"Total verses in file: {len(all_verses)}")
        else:
            print("No new unique verses found to add.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main() 