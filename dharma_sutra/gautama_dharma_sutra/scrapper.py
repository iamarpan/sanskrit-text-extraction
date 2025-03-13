import re
import json
def formatted_extract_verses():
    # Load the JSON data
    with open('output_chapters.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

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
                        "verse_number": formatted_verse_number
                    })


# Output the formatted verses to a JSON file
    with open('formatted_verses.json', 'w', encoding='utf-8') as outfile:
        json.dump(verses_list, outfile, ensure_ascii=False, indent=4) 

def extract_verses(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    verses_list = []
    for chapter in data:
        chapter_number = chapter["chapter_number"]
        for sub_chapter in chapter["sub_chapters"]:
            sub_chapter_number = sub_chapter["sub_chapter_number"]
            content = sub_chapter["content"]
            # Split content into verses using regex to match Hindi numbers
            verses = re.split(r'(?<=\\d)\\s+', content)
            # Iterate over the verses and their numbers
            for verse in verses:
                # Extract the verse number using regex
                match = re.search(r'(\d+)$', verse.strip())
                if match:
                    verse_number = match.group(0)
                    verse_text = re.sub(r'\\d+\\s*$', '', verse).strip()
                    # Format the verse number
                    formatted_verse_number = f"{chapter_number}.{sub_chapter_number}.{verse_number}"
                    verses_list.append({
                        "verse": verse_text,
                        "verse_number": "gautama_dharma_sutra->"+formatted_verse_number
                    })
    with open('verses_list.json', 'w', encoding='utf-8') as outfile:
        json.dump(verses_list, outfile, ensure_ascii=False, indent=4)

def extract_chapters(file_path):
    """
    Extracts chapters from a Markdown file where each chapter is identified by ':<hindi number>'.

    Parameters:
    - file_path (str): The path to the Markdown file.

    Returns:
    - list: A list of dictionaries, each containing the chapter number and its content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Regex pattern to match chapters
        chapter_pattern = r'(.*?)(?::([०१२३४५६७८९]+))\s*(?:\n|$)'
        chapter_matches = list(re.finditer(chapter_pattern, content, re.DOTALL))

        chapters = []
        last_chapter_end = 0

        for chapter_match in chapter_matches:
            chapter_content = chapter_match.group(1).strip()
            chapter_number = chapter_match.group(2).strip()

            if chapter_content:
                chapters.append({
                    "chapter_number": chapter_number,
                    "content": chapter_content
                })

            last_chapter_end = chapter_match.end()

        # Check for remaining content in the last chapter
        if last_chapter_end < len(content):
            remaining_chapter_content = content[last_chapter_end:].strip()
            if remaining_chapter_content:
                chapters.append({
                    "chapter_number": "unknown",
                    "content": remaining_chapter_content
                })

        print(f"Total chapters detected: {len(chapters)}")
        return chapters

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_sub_chapters(chapters):
    """
    Extracts sub-chapters from each chapter where each sub-chapter is identified by '::<hindi number>'.

    Parameters:
    - chapters (list): The list of chapters with their content.

    Returns:
    - list: A list of dictionaries, each containing the chapter number and its sub-chapters.
    """
    sub_chapter_pattern = r'(.*?)(?:>([०१२३४५६७८९]+))\s*(?:\n|$)'

    for chapter in chapters:
        chapter_content = chapter['content']
        sub_chapter_matches = list(re.finditer(sub_chapter_pattern, chapter_content, re.DOTALL))

        sub_chapters = []
        last_sub_chapter_end = 0

        for sub_chapter_match in sub_chapter_matches:
            sub_chapter_content = sub_chapter_match.group(1).strip()
            sub_chapter_number = sub_chapter_match.group(2).strip()

            if sub_chapter_content:
                sub_chapters.append({
                    "sub_chapter_number": sub_chapter_number,
                    "content": sub_chapter_content
                })

            last_sub_chapter_end = sub_chapter_match.end()

        # Check for remaining content in the last sub-chapter
        if last_sub_chapter_end < len(chapter_content):
            remaining_sub_chapter_content = chapter_content[last_sub_chapter_end:].strip()
            if remaining_sub_chapter_content:
                sub_chapters.append({
                    "sub_chapter_number": "unknown",
                    "content": remaining_sub_chapter_content
                })

        chapter['sub_chapters'] = sub_chapters
        del chapter['content']  # Remove the raw content as it's now split into sub-chapters

    return chapters

def write_chapters_to_json(chapters, output_file):
    """
    Writes the extracted chapters and sub-chapters to a JSON file.

    Parameters:
    - chapters (list): The list of chapters to write to the file.
    - output_file (str): The path to the output JSON file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(chapters, json_file, ensure_ascii=False, indent=4)
        print(f"Chapters and sub-chapters successfully written to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to JSON: {e}")

# Example usage
if __name__ == '__main__':
    input_file = "/Users/arpansrivastava/Development/BHERI/dharma_sutra/gautama_dharma_sutra/gautama_dharma_sutra.md"  # Update this to your actual file path
    output_json_file = "/Users/arpansrivastava/Development/BHERI/dharma_sutra/gautama_dharma_sutra/output_chapters.json"  # Update this to your desired output file path
    chapters = extract_chapters(input_file)

    if chapters:
        chapters_with_sub_chapters = extract_sub_chapters(chapters)
        write_chapters_to_json(chapters_with_sub_chapters, output_json_file)
    extract_verses(output_json_file)
    formatted_extract_verses()