import re
import json



def english_to_hindi_numerals(english_number: str) -> str:
    # Mapping of English numerals (0-9) to Hindi numerals (०-९)
    english_to_hindi_map = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }

    # Convert each digit in the input number
    hindi_number = ''.join(english_to_hindi_map.get(char, char) for char in english_number)

    return hindi_number
def extract_verses_from_md(input_file, output_file="verses_output.json"):
    # Read the file
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Split into paragraphs (verses are separated by an empty line)
    paragraphs = content.split("\n\n")
    adhyay = 0
    # Pattern to match verses ending with || verse number ||
    verse_pattern = re.compile(r'^(.*?)\s*॥\s*(\d+)\s*॥$', re.DOTALL)

    verses = []

    # Process each paragraph
    for paragraph in paragraphs:
        lines = paragraph.split("\n")  # Split into individual lines
        lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines

        if not lines:
            continue

        # Join lines into a single verse
        full_verse = " ".join(lines)

        # Match the verse pattern
        match = verse_pattern.match(full_verse)
        if match:
            verse_text, verse_number = match.groups()
            verse_text = " ".join(verse_text.split())  # Normalize spaces
            if verse_number=='१':
                adhyay+=1
            # Append to list
            verses.append({
                "verse": verse_text,
                "ref": f"naradeyadharmashartam->{english_to_hindi_numerals(str(adhyay))}.{verse_number}"
            })

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, ensure_ascii=False, indent=4)

    print(f"Verses successfully written to {output_file}")

# Example usage
if __name__ == '__main__':
    file_path='/Users/arpansrivastava/Development/BHERI/smRtiH/naradeyadharmashartam/naradeyadharmashartam.md'
    extract_verses_from_md(file_path)