import re
import json

def extract_verses(markdown_file):
    verses = []
    current_verse = []
    
    with open(markdown_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    for line in lines:
        line = line.strip()
        
        # If we encounter an empty line and have collected verse content
        if not line and current_verse:
            # Join all lines of the verse
            verse_text = ' '.join(current_verse)
            
            # Extract verse number if present
            verse_number = None
            verse_match = re.search(r'([०-९]+)$', verse_text)
            if verse_match:
                verse_number = verse_match.group(1)
                verse_text = verse_text[:-len(verse_number)].strip()
            
            # Create verse object
            verse_obj = {
                'verse_number': "lagadha_vedanga_jyotish->"+str(verse_number),
                'verse': verse_text,
                'verse_metadata': []
            }
            verses.append(verse_obj)
            current_verse = []
        # If line has content, add it to current verse
        elif line:
            current_verse.append(line)
    
    # Add the last verse if there is one
    if current_verse:
        verse_text = ' '.join(current_verse)
        verse_match = re.search(r'([०-९]+)$', verse_text)
        if verse_match:
            verse_number = verse_match.group(1)
            verse_text = verse_text[:-len(verse_number)].strip()
        
        verse_obj = {
            'verse_number': "lagadha_vedanga_jyotish->"+str(verse_number),
            'verse': verse_text,
            'verse_metadata': []
        }
        verses.append(verse_obj)
    
    return verses

def save_to_json(verses, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)

def main():
    input_file = 'lagadha_vedanga_jyotish.md'
    output_file = 'verses.json'
    
    verses = extract_verses(input_file)
    save_to_json(verses, output_file)
    print(f"Successfully extracted {len(verses)} verses and saved to {output_file}")

if __name__ == "__main__":
    main() 