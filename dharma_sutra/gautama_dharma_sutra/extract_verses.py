import json
import re

# Load the JSON data
with open('output_chapters.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to extract verses and their numbers
def extract_verses(data):
    verses_list = []
    for chapter in data:
        chapter_number = chapter["chapter_number"]
        for sub_chapter in chapter["sub_chapters"]:
            sub_chapter_number = sub_chapter_number = sub_chapter["sub_chapter_number"]
            content = sub_chapter["content"]
            # Split content into verses using regex to match Hindi numbers
            verses = re.split(r'(?<=\d)\s', content)
            # Iterate over the verses and their numbers
            for verse in verses:
                # Extract the verse number using regex
                match = re.search(r'(\d+)$', verse.strip())
                if match:
                    verse_number = match.group(0)
                    verse_text = re.sub(r'\d+\s*$', '', verse).strip()
                    # Format the verse number
                    formatted_verse_number = f"{chapter_number}.{sub_chapter_number}.{verse_number}"
                    verses_list.append({
                        "verse": verse_text,
                        "verse_number": "gautama_dharma_sutra->"+formatted_verse_number
                    })
    return verses_list

# Extract verses and write to a JSON file
verses_list = extract_verses(data)

# Output the formatted verses to a JSON file
with open('formatted_verses.json', 'w', encoding='utf-8') as outfile:
    json.dump(verses_list, outfile, ensure_ascii=False, indent=4) 