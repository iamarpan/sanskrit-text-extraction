import re
import json
from collections import defaultdict

def process_yogayatra_file(filename="yogayAtrA.md"):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split content into verses
        verses_dict = defaultdict(list)
        lines = content.split('\n')
        current_verse_num = None
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Check for verse number at start of line
            verse_num_match = re.match(r'^([१-९][०-९]*\.[१-९][०-९]?)\s+(.+)$', line)
            
            if verse_num_match:
                verse_num, verse_text = verse_num_match.groups()
                # Add the verse text to the appropriate verse number
                verses_dict[verse_num].append(verse_text)
            # We don't need an elif clause anymore since each line of a verse has its number
        
        # Format verses
        verses = []
        # Sort by chapter and verse number to maintain order
        for verse_num in sorted(verses_dict.keys(), key=lambda x: [int(n) for n in x.split('.')]):
            verses.append({
                "verse": " ".join(verses_dict[verse_num]),
                "verse_number": f"yogayAtrA->{verse_num}",
                "verse_metadata": []
            })
        
        return verses
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []

def main():
    verses = process_yogayatra_file()
    output_file = "yogayatra_verses.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"verses": verses}, f, ensure_ascii=False, indent=2)
        print(f"Successfully wrote verses to {output_file}")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

if __name__ == "__main__":
    main() 