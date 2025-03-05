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
            "ref": f"vashishtha_smriti->{english_to_hindi_numerals(str(adhyay))}.{verse_number}"
        })

# Write output to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, indent=4, ensure_ascii=False)

    print(f"Verses successfully extracted and saved to {output_file}")


def remove_ending_adhyay_text(input_json_file,output_json_file):
    # Read the JSON file
    with open(input_json_file, "r", encoding="utf-8") as file:
        verses = json.load(file)

    # Regex pattern to match "इति वासिष्ठे धर्मशास्त्रे<count>।"
    pattern =  r"इति वासिष्ठे धर्मशास्त्रे\s*[^।]+।"

    # Clean verses
    for verse in verses:
        verse["verse"] = re.sub(pattern, "", verse["verse"]).strip()

    # Write cleaned data back to JSON
    with open(output_json_file, "w", encoding="utf-8") as file:
        json.dump(verses, file, indent=4, ensure_ascii=False)

    print(f"Cleaned verses successfully saved to {output_json_file}")


def clean_starting_adhyay(input_json_file: str, output_json_file: str):
    """
    Reads a JSON file, removes everything before and including 'ऽध्यायः'
    from each verse, and writes the cleaned data to a new JSON file.

    :param input_json_file: Path to the input JSON file.
    :param output_json_file: Path to save the cleaned JSON file.
    """
    # Regex pattern to match everything before & including "ऽध्यायः"
    pattern = r"^.*ऽध्यायः\s*"

    # Read the JSON file
    with open(input_json_file, "r", encoding="utf-8") as file:
        verses = json.load(file)

    # Clean verses
    for verse in verses:
        old_text = verse["verse"]
        cleaned_text = re.sub(pattern, "", old_text).strip()  # Remove everything before "ऽध्यायः"
        cleaned_text = re.sub(r"^।\s*", "", cleaned_text)

        verse["verse"] = cleaned_text  # Update JSON object

    # Write cleaned data back to JSON
    with open(output_json_file, "w", encoding="utf-8") as file:
        json.dump(verses, file, indent=4, ensure_ascii=False)

    print(f"✅ Final cleaned verses saved to {output_json_file}")


# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/smRtiH/vashishtha_smriti/vasishtha_smriti.md"  # Update this to your actual file name
    input_json_file = "verses.json"
    output_json_file = "cleaned_verses.json"
    create_verses(input_file)
    remove_ending_adhyay_text(input_json_file,output_json_file)
    clean_starting_adhyay(output_json_file,"final_result.json")