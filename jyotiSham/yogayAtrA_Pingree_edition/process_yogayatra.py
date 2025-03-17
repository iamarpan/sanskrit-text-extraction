import json
import re

def hindi_to_arabic(hindi_num):
    # Dictionary to convert Hindi numerals to Arabic
    hindi_arabic = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    return ''.join(hindi_arabic.get(c, c) for c in hindi_num)

def process_yogayatra_file(file_path):
    verses = {}
    current_adhyay = None
    current_adhyay_name = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for अध्याय header
        if line.startswith('अध्याय'):
            parts = line.split()
            if len(parts) >= 3:
                current_adhyay = parts[1]
                current_adhyay_name = ' '.join(parts[2:])
            continue
            
        # Check for verse number
        verse_match = re.match(r'(\d+\.\d+)', line)
        if verse_match:
            verse_number = verse_match.group(1)
            verse_text = line[line.index(verse_number) + len(verse_number):].strip()
            
            if verse_number in verses:
                # Append to existing verse with newline
                verses[verse_number]["verse"] += "\n" + verse_text
            else:
                # Create new verse entry
                verses[verse_number] = {
                    "verse": verse_text,
                    "verse_number": f"yogayAtrA_Pingree_edition.md->{verse_number}",
                    "verse_metadata": [f"अध्याय :{current_adhyay_name}"]
                }
    
    # Convert dictionary to list and sort by verse number
    verse_list = list(verses.values())
    
    # Custom sorting function that converts Hindi numerals to Arabic for comparison
    def sort_key(x):
        verse_num = x["verse_number"].split("->")[1]
        chapter, verse = verse_num.split(".")
        return (int(hindi_to_arabic(chapter)), int(hindi_to_arabic(verse)))
    
    verse_list.sort(key=sort_key)
    return verse_list

# Process the file and generate JSON
verses = process_yogayatra_file('yogayAtrA_Pingree_edition.md')

# Write to JSON file
with open('yogayatra_verses.json', 'w', encoding='utf-8') as f:
    json.dump(verses, f, ensure_ascii=False, indent=2) 