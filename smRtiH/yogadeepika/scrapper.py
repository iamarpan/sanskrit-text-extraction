import re
import json


def english_to_hindi_numerals(number):
    hindi_numerals = {"0": "०", "1": "१", "2": "२", "3": "३", "4": "४", "5": "५", "6": "६", "7": "७", "8": "८",
                      "9": "९"}
    return "".join(hindi_numerals[digit] for digit in number)


def clean_verse(verse_text):
    if "पटलः" in verse_text:
        last_patala_index = verse_text.rfind("पटलः")
        verse_text = verse_text[last_patala_index + len("पटलः"):].strip()
    return verse_text
def parse_md_file(filename, output_filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    chapters = re.split(r'इति योगदीपिकायां', content)
    adhyay = 1
    verses=[]
    print(len(chapters))
    for chapter in chapters:
        chapter = chapter.strip()
        verses_in_chapter = re.findall(r'(.*?)(?:॥\s*(\d+)\s*॥)', chapter, re.DOTALL)

        for verse_text, verse_number in verses_in_chapter:
            verse_text = clean_verse(verse_text.strip())

            verses.append({
                "verse": verse_text,
                "ref": f"yogadeepika->{english_to_hindi_numerals(str(adhyay))}.{verse_number}"
            })

        adhyay += 1

    with open(output_filename, 'w', encoding='utf-8') as out_file:
        json.dump(verses, out_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    filepath= '/Users/arpansrivastava/Development/BHERI/smRtiH/yogadeepika/yogadeepika.md'
    parse_md_file(filepath,"verses_output.json")