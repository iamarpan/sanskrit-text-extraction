import re
import json

def english_to_hindi_numerals(number):
    hindi_numerals = {"0": "०", "1": "१", "2": "२", "3": "३", "4": "४", "5": "५", "6": "६", "7": "७", "8": "८",
                      "9": "९"}
    return "".join(hindi_numerals[digit] for digit in number)

def extract_verses_from_md(input_file, output_file="verses_output.json"):
    # Read the file
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Split into paragraphs (verses are separated by an empty line)
    paragraphs = content.split("\n\n")

    # Pattern to match verses ending with a number
    verse_pattern = re.compile(r'^(.*)\s(\d+)$', re.DOTALL)

    verses = []
    adhyay=0
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
            if verse_number == '१':
                adhyay+=1
            # Append to list
            verses.append({
                "verse": verse_text,
                "ref": f"vishwamitra_smriti->{english_to_hindi_numerals(str(adhyay))}.{verse_number}"
            })

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, ensure_ascii=False, indent=4)

    print(f"Verses successfully written to {output_file}")

# Example usage
if __name__ == '__main__':
    file_path = "/Users/arpansrivastava/Development/BHERI/smRtiH/vishwamitra_smriti/vishvamitra_smriti.md"
    extract_verses_from_md(file_path)
