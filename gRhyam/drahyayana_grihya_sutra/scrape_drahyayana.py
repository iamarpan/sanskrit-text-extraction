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

def patals(md_file):
    with open(md_file, 'r', encoding='utf-8') as file:
        content = file.read()

    patals = []

    # Match "इति <ordinal> पटलः" at the end of a Patala
    pattern = r'(.*?)\s*इति\s*(प्रथमः|द्वितीयः|तृतीय|चतुर्थः|पञ्चमः|षष्ठः|सप्तमः|अष्टमः|नवमः|दशमः)\s+पटलः\s*(?:\n|$)'

    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        return [{"patala": 1, "content": content.strip()}]

    for i, match in enumerate(matches):
        patala_content = match.group(1).strip()  # Directly use match group(1)
        patala_name = match.group(2).strip()  # Extract Patala name

        if patala_content:  # Avoid empty sections
            patals.append({
                "patala": i + 1,  # Assign Patala number starting from 1
                "content": patala_content
            })
        print(f"Detected पटलः {i + 1}: {patala_name}")

    print(f"Total पटलः detected: {len(patals)}")
    return patals


def split_khands(adhyaya_data):
    # Updated regex to capture Khand markers at the end of the content
    khand_pattern = r'(.*?)\s*इति\s*(प्रथमः|द्वितीयः|तृतीयः|चतुर्थः|पञ्चमः|षष्ठः|सप्तमः|अष्टमः|नवमः|दशमः)\s+खण्डः\s*(?:\n|$)'
    matches = list(re.finditer(khand_pattern, adhyaya_data['content'], re.DOTALL))

    khands = []
    for i, match in enumerate(matches):
        khand_content = match.group(1).strip()  # Extract content before the marker
        khand_name = match.group(2).strip()  # Extract the ordinal number

        if khand_content:  # Avoid empty sections
            khands.append({
                "khand_text": khand_name,
                "khand": i + 1,  # Sequential numbering for Khands
                "content": khand_content
            })

    print(f"Total खण्डः detected: {len(khands)}")
    return khands

def split_verses(khand_data, adhyaya_number):
    # Regex pattern to match verses ending with a number
    verse_pattern = r'([\s\S]+?)\s([०१२३४५६७८९]+)'  # Match verses ending with a Hindi numeral
    matches = list(re.finditer(verse_pattern, khand_data['content']))

    verses = []
    for match in matches:
        verse_text = match.group(1).strip()
        verse_number = match.group(2).strip()

        verses.append({
            "verse": verse_text,
            "verse_number": f"drahyayana_grihya_sutra->{english_to_hindi_numerals(str(adhyaya_number))}.{english_to_hindi_numerals(str(khand_data['khand']))}.{verse_number}"
        })

    return verses


def process_document(md_file):
    adhyayas = patals(md_file)
    final_output = []

    for adhyaya_data in adhyayas:
        print(adhyaya_data['patala'],"----")
        khands = split_khands(adhyaya_data)
        for khand_data in khands:
            verses = split_verses(khand_data, adhyaya_data['patala'])
            final_output.extend(verses)  # Collect all verses in final output

    return final_output


# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/drahyayana_grihya_sutra/drahyayana_grihya_sutra.md"  # Update this to your actual file name
    input_json_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/drahyayana_grihya_sutra/verses.json"
    output_json_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/drahyayana_grihya_sutra/cleaned_verses.json"
    output = process_document(input_file)
    with open("/Users/arpansrivastava/Development/BHERI/gRhyam/drahyayana_grihya_sutra/output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("Processing complete! Output saved to 'output.json'.")

    #split_khands(adhyays)

    #create_verses(adhyays)