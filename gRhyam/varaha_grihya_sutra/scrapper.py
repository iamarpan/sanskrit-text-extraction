import re
import json

# Convert English numerals to Hindi numerals
def english_to_hindi_numerals(num_str):
    hindi_numerals = {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५',
                      '6': '६', '7': '७', '8': '८', '9': '९'}
    return ''.join(hindi_numerals[digit] for digit in num_str)

# Read input Markdown file
def create_verses(input_file):
    output_file = "verses.json"

    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()

    verses = []
    adhyay = 0  # Assuming this is the first chapter

# Match verses ending with a number
    matches = re.findall(r'([\s\S]+?)\s(\d+)', text)

    for match in matches:
        verse_text = match[0].strip()
        verse_number = match[1]
        if verse_number == '१':
            adhyay += 1
        verses.append({
            "verse": verse_text,
            "ref": f"varaha_grihya_sutra->{english_to_hindi_numerals(str(adhyay))}.{verse_number}"
        })

# Write output to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, indent=4, ensure_ascii=False)

    print(f"Verses successfully extracted and saved to {output_file}")

def clean_khanda_text(input_json="verses.json", output_json="processed_verses.json"):
    # Read the JSON file
    with open(input_json, "r", encoding="utf-8") as file:
        verses = json.load(file)

    # Process each verse
    for verse in verses:
        if "verse" in verse and "खण्डम्" in verse["verse"]:
            # Find the position of खण्डम् and remove everything before and including it
            khanda_pos = verse["verse"].find("खण्डम्")
            verse["verse"] = verse["verse"][khanda_pos + len("खण्डम्"):].strip()

    # Write the processed verses back to a new JSON file
    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(verses, file, indent=4, ensure_ascii=False)

    print(f"Verses processed and saved to {output_json}")

# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/varaha_grihya_sutra/varaha_grihya_sutra.md"  # File is in the same directory
    input_json_file = "verses.json"
    output_json_file = "cleaned_verses.json"
    create_verses(input_file)
    clean_khanda_text(input_json_file, "processed_verses.json")