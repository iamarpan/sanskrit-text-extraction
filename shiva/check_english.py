import json
import re
import os

def contains_english(text):
    """Check if text contains English characters."""
    return bool(re.search(r'[A-Za-z]', text))

def check_verses_for_english(json_file):
    """Check all verses in a JSON file for English text."""
    print(f"\nChecking {json_file} for English text...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            verses = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file}.")
        return
    
    english_verses = []
    for verse in verses:
        if contains_english(verse['verse']):
            english_verses.append({
                'ref': verse['ref'],
                'verse': verse['verse'],
                'document_link': verse['document_link']
            })
    
    if english_verses:
        print(f"\nFound {len(english_verses)} verses containing English text:")
        for verse in english_verses:
            print(f"\nReference: {verse['ref']}")
            print(f"Document: {verse['document_link']}")
            print("Verse text:")
            print(verse['verse'])
            print("-" * 80)
    else:
        print("No English text found in any verses.")

def main():
    # Check all extracted_verses-*.json files in the current directory
    #json_files = [f for f in os.listdir('.') if f.startswith('extracted_verses-') and f.endswith('.json')]
    json_files = ['output.json']
    if not json_files:
        print("No extracted verses JSON files found in the current directory.")
        return
    
    for json_file in sorted(json_files):
        check_verses_for_english(json_file)

if __name__ == "__main__":
    main() 
