import re
import json

# Convert English numerals to Hindi numerals
def english_to_hindi_numerals(num_str):
    hindi_numerals = {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५',
                      '6': '६', '7': '७', '8': '८', '9': '९'}
    return ''.join(hindi_numerals[digit] for digit in num_str)

# Read input Markdown file


def patalas(data):

    patalas = []

    # Match "इति <ordinal> पटलः" at the end of a Patala
    pattern = r'(.*?)\s*(प्रथमः|द्वितीयः|तृतीयः|चतुर्थः|पञ्चमः|षष्ठः|सप्तमः|अष्टमः|नवमः|दशमः)\s+पटलः\s*(?:\n|$)'

    matches = list(re.finditer(pattern, data, re.DOTALL))

    if not matches:
        return [{"patala": 1, "content": data.strip()}]

    for i, match in enumerate(matches):
        patalas_content = match.group(1).strip()  # Directly use match group(1)
        patalas_name = match.group(2).strip()  # Extract Patala name
        
        if patalas_content:  # Avoid empty sections
            patalas.append({
                "patalas": i + 1,  # Assign Patala number starting from 1
                "content": patalas_content
            })
        #print(f"Detected प्रपाठकः {i + 1}: {prapathakas_name}")

    print(f"Total प्रपाठकः detected: {len(patalas)}")
    return patalas



def split_khands(adhyaya_data):
    # Updated regex to capture lines with only Hindi numerals indicating the end of a khand
    khand_pattern = r'(.*?)\n([०१२३४५६७८९]+)\s*(?:\n|$)'
    matches = list(re.finditer(khand_pattern, adhyaya_data['content'], re.DOTALL))

    khands = []
    last_end = 0  # Track the end of the last match

    for i, match in enumerate(matches):
        khand_content = match.group(1).strip()  # Extract content before the numeral
        khand_number = match.group(2).strip()  # Extract the Hindi numeral

        if khand_content:  # Avoid empty sections
            khands.append({
                "khand_number": khand_number,
                "khand": i + 1,  # Sequential numbering for Khands
                "content": khand_content
            })

        last_end = match.end()  # Update the end position

    # Check if there's remaining content after the last match
    if last_end < len(adhyaya_data['content']):
        remaining_content = adhyaya_data['content'][last_end:].strip()
        if remaining_content:
            khands.append({
                "khand_number": "unknown",  # Assign a placeholder number
                "khand": len(khands) + 1,  # Sequential numbering for Khands
                "content": remaining_content
            })

    print(f"Total खण्डः detected: {len(khands)}")
    return khands

def split_verses(khand_data, question_number,patal_number,khand_number):
    # Regex pattern to match verses ending with a number
    verse_pattern = r'([\s\S]+?)\s([०१२३४५६७८९]+)'  # Match verses ending with a Hindi numeral
    matches = list(re.finditer(verse_pattern, khand_data['content']))

    verses = []
    for match in matches:
        verse_text = match.group(1).strip()
        verse_number = match.group(2).strip()

        verses.append({
            "verse": verse_text,
            "verse_number": f"hiranyakeshi_grihya_sutra->{english_to_hindi_numerals(str(question_number))}.{english_to_hindi_numerals(str(patal_number))}.{english_to_hindi_numerals(str(khand_number))}.{verse_number}"
        })

    return verses

def split_document_file_by_delimiter(file_path, delimiter="प्रथमः प्रश्नः समाप्तः"):
    """
    Reads a file and splits its content into two parts using the specified delimiter.

    Parameters:
    - file_path (str): The path to the file to be read and split.
    - delimiter (str): The delimiter to use for splitting the document.

    Returns:
    - list: A list containing the two parts of the document, or None if the delimiter is not found exactly once.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Split the content using the specified delimiter
        parts = content.split(delimiter)
        
        # Check if the split resulted in exactly two parts
        if len(parts) != 2:
            print("The document does not contain the delimiter exactly once.")
            return None
        
        # Return the two parts as a list
        return [parts[0].strip(), parts[1].strip()]

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def process_document(md_file):
    questions = split_document_file_by_delimiter(md_file)
    final_output = []
    for index,question in enumerate(questions):
        patals = patalas(question)
        for patal in patals:
            khands = split_khands(patal)
            for khand in khands:
                verses = split_verses(khand,index+1,patal['patalas'],khand['khand'])
                final_output.extend(verses)  # Collect all verses in final output

    return final_output


# Example usage

if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/hiranyakeshi_grihya_sutra/hiranyakeshi_grihya_sutra.md"  # Update this to your actual file name
    input_json_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/hiranyakeshi_grihya_sutra/verses.json"
    output_json_file = "/Users/arpansrivastava/Development/BHERI/gRhyam/hiranyakeshi_grihya_sutra/cleaned_verses.json"
    output = process_document(input_file)
    with open("/Users/arpansrivastava/Development/BHERI/gRhyam/hiranyakeshi_grihya_sutra/output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("Processing complete! Output saved to 'output.json'.")

    #split_khands(adhyays)

    #create_verses(adhyays)
