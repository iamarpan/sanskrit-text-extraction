import json
import re

def parse_verses(md_file):
    verses = {}
    current_verse_number = None
    
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains verse number (format: १.०१)
        verse_match = re.match(r'^(\d+\.\d+)\s*:', line)
        if verse_match:
            current_verse_number = verse_match.group(1)
            # Get the verse text after the verse number and colon
            verse_text = line.split(':', 1)[1].strip()
            
            # Format verse number with prefix (without extra quotes)
            formatted_verse_number = f'sUryasiddhAntaH_pAThAntaropetaH->{current_verse_number}'
            
            # Initialize or append to existing verse
            if current_verse_number not in verses:
                verses[current_verse_number] = {
                    "verse": verse_text,
                    "verse_number": formatted_verse_number,
                    "verse_metadata": []
                }
            else:
                verses[current_verse_number]["verse"] += "\n" + verse_text
    
    # Convert dictionary to list
    return list(verses.values())

def main():
    input_file = "sUryasiddhAntaH_pAThAntaropetaH.md"
    output_file = "verses.json"
    
    verses = parse_verses(input_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main() 