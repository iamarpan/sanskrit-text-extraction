import re
from tqdm import tqdm
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
def process_file(input_file, output_file):

    # Read the file content
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Pattern to match each paragraph ending with a Hindi numeral
    pattern = r"(.*?)(\d+)\s*(?=\n\n|\Z)"

    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL)

    # Prepare output content
    output_content = ""
    for paragraph, number in matches:
        output_content += f"{paragraph.strip()} {number}\n\n"

    # Write to the output file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(output_content)

    print(f"Output written to '{output_file}'.")
    return True


def extract_paragraphs(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # Split paragraphs based on empty lines
    paragraphs = re.split(r'^\s*$\n', content, flags=re.MULTILINE)

    # Remove empty strings and strip whitespace
    paragraphs = [para.strip() for para in paragraphs if para.strip()]

    # Display the paragraphs
    return paragraphs


# Function to convert English numerals to Hindi numerals for adhyay only
def english_to_hindi_numerals(number_str):
    hindi_numerals = "०१२३४५६७८९"
    return "".join(hindi_numerals[int(digit)] for digit in number_str)

def extract_verses_from_paragraphs(paragraphs, output_file="verses_output.json"):
    # Compile regex patterns
    verse_pattern = re.compile(r'^(.*?)(\s\d+)\s*$')
    paragraph_number_pattern = re.compile(r'^(\d+)\s*$')

    # Initialize variables
    adhyay = 0
    verses = []
    current_verse_text = []
    current_verse_number = None
    current_paragraph_number = None

    # Process each paragraph
    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]

        # Identify paragraph number from the last line if it matches the pattern
        if lines and paragraph_number_pattern.match(lines[-1]):
            current_paragraph_number = paragraph_number_pattern.match(lines[-1]).group(1)

        # Check for new adhyay based on paragraph number
        if current_paragraph_number == '१':
            adhyay += 1

        for line in lines:
            match = verse_pattern.match(line)
            if match:
                verse_text, verse_number = match.groups()

                # If a new verse is found, save the previous verse if it exists
                if current_verse_text and current_verse_number:
                    verses.append({
                        "verse": " ".join(current_verse_text),
                        "ref": f"ashvalayana_shrauta_sutra->{english_to_hindi_numerals(str(adhyay))}.{current_paragraph_number}.{current_verse_number}"
                    })
                    current_verse_text = []

                # Start a new verse
                current_verse_text.append(verse_text.strip())
                current_verse_number = verse_number.strip()

            else:
                # If no verse number, accumulate for the next verse
                current_verse_text.append(line)

        # Append the last accumulated verse
        if current_verse_text and current_verse_number:
            verses.append({
                "verse": " ".join(current_verse_text),
                "ref": f"ashvalayana_shrauta_sutra->{english_to_hindi_numerals(str(adhyay))}.{current_paragraph_number}.{current_verse_number}"
            })
            current_verse_text = []

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, ensure_ascii=False, indent=4)

    print(f"Verses successfully written to {output_file}")


# Example usage
if __name__ == '__main__':
    result = extract_paragraphs("/Users/arpansrivastava/Development/BHERI/ashvalayana_shrauta_sutra/cleaned_output.md")
    extract_verses_from_paragraphs(result)

