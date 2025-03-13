import re
import json

# Define the file paths
markdown_file_path = 'vasishtha_dharma_sutra.md'
output_file_path = 'formatted_verses.json'

# Define the pattern to identify chapter endings with verse numbers
chapter_end_pattern = r'इति वासिष्ठधर्मशास्त्रे\s*.*?ऽध्यायः\s*(\d+)'  # Matches the chapter ending pattern
verse_pattern = r'(\d+)\s*\n'  # Matches the verse number pattern

# Read the entire Markdown file
with open(markdown_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Find all chapter endings
chapter_endings = list(re.finditer(chapter_end_pattern, content))

# Extract chapters
chapters = {}
start_index = 0
for i, match in enumerate(chapter_endings):
    end_index = match.end()
    chapter_number = match.group(1)
    chapter_text = content[start_index:end_index].strip()
    # Clean the chapter text
    chapter_text = re.sub(r'इति वासिष्ठधर्मशास्त्रे\s*.*?ऽध्यायः\s*\d+', '', chapter_text)
    chapters[f'Chapter {chapter_number}'] = chapter_text
    start_index = end_index

# Define a function to split chapter text into verses
def split_into_verses(text):
    # Split the text by lines ending with a Hindi number
    verses = re.split(r'(\d+)\s*\n', text)
    return [(verses[i].strip(), verses[i+1].strip()) for i in range(0, len(verses)-1, 2)]

# Format the verses
formatted_verses = []
for chapter, text in chapters.items():
    chapter_number = chapter.split()[-1]  # Extract chapter number
    verses = split_into_verses(text)
    for verse_text, verse_number in verses:
        formatted_verses.append({
            'verse': verse_text,
            'verse_number': f'vasishtha_dharma_sutra->{chapter_number}.{verse_number}'
        })

# Save formatted verses to JSON
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(formatted_verses, json_file, ensure_ascii=False, indent=4)

print(f'Formatted verses saved to {output_file_path}')
