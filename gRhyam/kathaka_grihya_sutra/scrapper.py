import re
import json

# Convert English numerals to Hindi numerals
def english_to_hindi_numerals(num_str):
    hindi_numerals = {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५',
                      '6': '६', '7': '७', '8': '८', '9': '९'}
    return ''.join(hindi_numerals[digit] for digit in num_str)

# Read input Markdown file
def create_verses(adhyays):
    output_file = "verses.json"

    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()

    verses = []
     # Assuming this is the first chapter
# Match verses ending with a number
    for adhyay_index,adhyaya_data in enumerate(adhyays):

        subadhyay =0
        matches = re.findall(r'([\s\S]+?)\s(\d+)', adhyaya_data['content'])

        for match in matches:
            verse_text = match[0].strip()
            verse_number = match[1]
            if verse_number == '१':
                subadhyay += 1
            verses.append({
                "verse": verse_text,
                "ref": f"kathaka_grihya_sutra->{english_to_hindi_numerals(str(adhyay_index+1))}.{english_to_hindi_numerals(str(subadhyay))}.{verse_number}"
            })

# Write output to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, indent=4, ensure_ascii=False)

    print(f"Verses successfully extracted and saved to {output_file}")



def split_adhyays(md_file):
    with open(md_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    adhyays = []
    current_content = []
    current_adhyay = None

    for line in lines:
        match = re.search(r'इति लौगाक्षिसूत्रे गृह्यपञ्चिकायां\s*(.*)', line)
        if match:
            current_adhyay = match.group(1).strip()  # Extract the adhyay name
            current_content.append(line)  # Include the ending line in content
            adhyays.append({'adhyay': current_adhyay, 'content': ''.join(current_content)})
            current_content = []  # Reset for the next adhyay
        else:
            current_content.append(line)

    return adhyays



# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/kathaka_grihya_sutra/kathaka_grihya_sutra.md"  # Update this to your actual file name
    input_json_file = "verses.json"
    output_json_file = "cleaned_verses.json"
    adhyays = split_adhyays(input_file)
    create_verses(adhyays)