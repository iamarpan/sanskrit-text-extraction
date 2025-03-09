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
                "ref": f"kaushitaka_grihya_sutra->{english_to_hindi_numerals(str(subadhyay))}.{verse_number}"
            })

# Write output to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(verses, json_file, indent=4, ensure_ascii=False)

    print(f"Verses successfully extracted and saved to {output_file}")



import re

def split_khands(md_file):
    with open(md_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    adhyays = []
    current_content = []
    current_adhyay = None

    for line in lines:
        match = re.search(r'अथ\s*(.*?)\s*खण्डः', line)
        if match:
            if current_content:
                # Save the previous Adhyay before starting a new one
                adhyays.append({'adhyay': current_adhyay, 'content': ''.join(current_content)})

            current_adhyay = match.group(1).strip()  # Extract the adhyay name
            current_content = [line]  # Start new content with the matched line
        else:
            current_content.append(line)

    # Append the last adhyay if there's any content left
    if current_content:
        adhyays.append({'adhyay': current_adhyay, 'content': ''.join(current_content)})

    return adhyays

import re

import re

import re

import re

import re


def split_adhyays(md_file):
    with open(md_file, 'r', encoding='utf-8') as file:
        content = file.read()

    adhyays = []

    # Match "इति कौषीतकगृह्ये <adhyay>" at the end of an Adhyaya
    pattern = r'(.*?)\s*इति कौषीतकगृह्ये\s*(.*?)\s*(?:\n|$)'

    matches = list(re.finditer(pattern, content, re.DOTALL))


    if not matches:
        return [{"adhyaya": 1, "content": f"अथ {content.strip()}"}]

    for i, match in enumerate(matches):
        adhyaya_content = match.group(1).strip()  # Directly use match group(1)
        adhyaya = match.group(2).strip()  # Extract Adhyaya name

        # Debugging Prints

        if adhyaya_content:  # Avoid empty sections
            adhyays.append({
                "adhyaya": i + 1,  # Assign Adhyaya number starting from 1
                "content": f"अथ {adhyaya_content}"
            })


    return adhyays

def split_khands(adhyaya_data):
    # Updated regex to capture Khand markers
    khand_pattern = r'अथ\s*([\s\S]+?)\s*खण्डः'
    matches = list(re.finditer(khand_pattern, adhyaya_data['content'], re.DOTALL))

    khands = []
    for i, match in enumerate(matches):
        khand_text = match.group(1).strip()  # Extract text after "अथ"

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(adhyaya_data['content'])
        khand_content = adhyaya_data['content'][start:end].strip()

        khands.append({
            "khand_text": khand_text,
            "khand": i + 1,  # Sequential numbering for Khands
            "content": khand_content
        })

    return khands

def split_verses(khand_data, adhyaya_number):
    verse_pattern = r'([\s\S]+?)\s(\d+)'  # Match verses ending with a number
    matches = list(re.finditer(verse_pattern, khand_data['content']))

    verses = []
    for match in matches:
        verse_text = match.group(1).strip()
        verse_number = match.group(2).strip()

        verses.append({
            "verse": verse_text,
            "verse_number": f"{english_to_hindi_numerals(str(adhyaya_number))}.{english_to_hindi_numerals(str(khand_data['khand']))}.{verse_number}"
        })

    return verses


def process_document(md_file):
    adhyayas = split_adhyays(md_file)
    final_output = []

    for adhyaya_data in adhyayas:
        khands = split_khands(adhyaya_data)

        for khand_data in khands:
            verses = split_verses(khand_data, adhyaya_data['adhyaya'])
            final_output.extend(verses)  # Collect all verses in final output

    return final_output


# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/kaushitaka_grihya_sutra/kaushitaka_grihya_sutra.md"  # Update this to your actual file name
    input_json_file = "verses.json"
    output_json_file = "cleaned_verses.json"
    output = process_document(input_file)
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("Processing complete! Output saved to 'output.json'.")

    #split_khands(adhyays)

    #create_verses(adhyays)