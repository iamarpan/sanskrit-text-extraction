import os
import re
import json
def read_markdown_file(file_path):
    """Reads the content of a Markdown (.md) file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_hindi_text(text):
    lines = text.strip().split("\n")
    formatted_verses = []
    temp_verses = []  # Store lines for the current paragraph
    paragraph_number = None  # To track the correct paragraph number

    for line in lines:
        line = line.strip()

        # Check if this line is a paragraph number (standalone number)
        if re.fullmatch(r"\d+", line):
            paragraph_number = line  # Store paragraph number

            # Assign stored verses to the detected paragraph number
            for verse_text, verse_number in temp_verses:
                formatted_verses.append({
                    "verse": " ".join(verse_text.split()),  # Normalize spaces
                    "ref": f"Baudhayana_Shulba_Sutra->{paragraph_number}.{verse_number}"
                })

            # Clear temp storage for the next paragraph
            temp_verses = []
            continue  # Skip adding this line as a verse

        # Match a verse ending with a number (indicating verse number)
        match = re.search(r"(\d+)\s*$", line)
        if match:
            verse_number = match.group(1)  # Extract verse number
            verse_text = line[:match.start()].strip()  # Extract verse text

            # Store the verse temporarily until we get the paragraph number
            temp_verses.append((verse_text, verse_number))

    return formatted_verses

if __name__ == "__main__":
    file_path = "/Users/arpansrivastava/Development/BHERI/Baudhayana_Shulba_Sutra.md"  # Replace with your file path
    file_path = "/Users/arpansrivastava/Development/BHERI-scrapper/sanskrit-text-extraction/baudhayan_shulba_sutra/Baudhayana_Shulba_Sutra.md"

    try:
        text = read_markdown_file(file_path)
        structured_verses = parse_hindi_text(text)
        print("total_verses",len(structured_verses))
        # Print JSON output
        with open("output.json", "w", encoding="utf-8") as json_file:
            json.dump(structured_verses, json_file, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error: {e}")
