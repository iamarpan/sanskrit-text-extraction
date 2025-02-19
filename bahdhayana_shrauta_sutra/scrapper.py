import re
import json
from tqdm import tqdm


def english_to_hindi_numerals(english_number: str) -> str:
    # Mapping of English numerals (0-9) to Hindi numerals (०-९)
    english_to_hindi_map = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }

    # Convert each digit in the input number
    hindi_number = ''.join(english_to_hindi_map.get(char, char) for char in english_number)

    return hindi_number



def extract_paragraphs(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split paragraphs based on any word followed by 'प्रश्नः'
    paragraphs = re.split(r'\n\S+ प्रश्नः\n', content)[1:]  # Skip first empty split

    return [para.strip() for para in paragraphs if para.strip()]

def extract_verses(paragraph):
    # Match verses ending with Sanskrit numbers (१, २, ३, etc.), ensuring numbers are preceded and followed by a space
    verse_pattern = re.findall(r'([\s\S]*?)\s+([१२३४५६७८९०]+)(?:\s+|$)', paragraph)
    verses = [(re.sub(r'\n+', '\n', verse.strip()), num) for verse, num in
              verse_pattern]  # Replace multiple \n with a single \n
    return verses



def generate_json(filename, output_filename):
    paragraphs = extract_paragraphs(filename)
    json_output = []

    for i, paragraph in enumerate(tqdm(paragraphs, desc="Processing Paragraphs"), 1):  # Paragraph numbers start from 1
        verses = extract_verses(paragraph)
        for verse, verse_num in verses:
            json_output.append({
                "verse": verse,
                "ref": f"Baudhayana_shrauta_sutra->{english_to_hindi_numerals(str(i))}.{verse_num}"
            })

    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_output, json_file, ensure_ascii=False, indent=4)


# Example usage
if __name__ == '__main__':
    filename = "/Users/arpansrivastava/Development/BHERI/bahdhayana_shrauta_sutra/baudhayana_shrauta_sutra.md"
    output_filename = "output.json"
    generate_json(filename, output_filename)
