import json
import re

def process_verses(markdown_file):
    verses_dict = {}  # Dictionary to store verses by their number
    current_verse = []
    current_number = None
    
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a Hindi numeral
        match = re.match(r'^(\d+)\s+(.*)', line)
        if match:
            # If we have a previous verse, save it
            if current_number is not None:
                verse_text = "\n".join(current_verse)
                if current_number in verses_dict:
                    # Merge with existing verse
                    verses_dict[current_number]["verse"] += "\n" + verse_text
                else:
                    # Create new verse entry
                    verses_dict[current_number] = {
                        "verse_number": f"vivAhapaTala->{current_number}",
                        "verse": verse_text,
                        "verse_metadata": []
                    }
            
            # Start new verse
            current_number = match.group(1)
            current_verse = [match.group(2)]
        else:
            # Continue current verse
            current_verse.append(line)
    
    # Add the last verse
    if current_number is not None:
        verse_text = "\n".join(current_verse)
        if current_number in verses_dict:
            # Merge with existing verse
            verses_dict[current_number]["verse"] += "\n" + verse_text
        else:
            # Create new verse entry
            verses_dict[current_number] = {
                "verse_number": f"vivAhapaTala->{current_number}",
                "verse": verse_text,
                "verse_metadata": []
            }
    
    # Convert dictionary to list and sort by verse number
    verses = sorted(verses_dict.values(), key=lambda x: int(x["verse_number"].split("->")[1]))
    
    # Create the final JSON structure
    json_structure = {
        "verses": verses
    }
    
    # Write to JSON file
    with open('verses.json', 'w', encoding='utf-8') as f:
        json.dump(json_structure, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_verses('vivAhapaTala.md') 
