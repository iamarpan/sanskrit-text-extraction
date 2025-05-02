#!/usr/bin/env python3
import os
import json
import glob
import re
from tqdm import tqdm

def clean_verse(verse_text):
    """
    Clean verse according to specified criteria.
    Returns (cleaned_verse, is_modified, modification_details)
    """
    original_verse = verse_text
    modification_details = []
    
    # Check and remove (<word>) from start of verse
    parentheses_match = re.match(r'^\s*\(([^)]+)\)\s*(.*)$', verse_text)
    if parentheses_match:
        removed_text = parentheses_match.group(1)
        verse_text = parentheses_match.group(2)
        modification_details.append({
            "type": "removed_parentheses",
            "removed_text": f"({removed_text})",
            "position": "start"
        })
    
    # Check and remove single word followed by - and \n at start
    dash_match = re.match(r'^([^\s-]+)\s*-\s*[\n\r]+(.*)$', verse_text, re.DOTALL|re.MULTILINE)
    if dash_match:
        removed_text = dash_match.group(1)
        verse_text = dash_match.group(2)
        modification_details.append({
            "type": "removed_dash_prefix",
            "removed_text": f"{removed_text}-",
            "position": "start"
        })
    
    is_modified = original_verse != verse_text
    return verse_text.strip(), is_modified, modification_details

def process_batch(input_file, output_dir, modified_dir):
    """Process a single batch file."""
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            verses = json.load(f)
        
        # Track modified verses
        modified_verses = []
        
        # Process each verse
        for verse in verses:
            cleaned_verse, is_modified, modification_details = clean_verse(verse['verse'])
            
            if is_modified:
                modified_info = {
                    'ref': verse['ref'],
                    'document_link': verse['document_link'],
                    'original_verse': verse['verse'],
                    'modified_verse': cleaned_verse,
                    'modifications': modification_details
                }
                modified_verses.append(modified_info)
            
            # Update the verse with cleaned version
            verse['verse'] = cleaned_verse
        
        # Save processed verses
        output_file = os.path.join(output_dir, os.path.basename(input_file))
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, ensure_ascii=False, indent=2)
        
        # Save modified verses if any
        if modified_verses:
            modified_file = os.path.join(modified_dir, os.path.basename(input_file))
            with open(modified_file, 'w', encoding='utf-8') as f:
                json.dump(modified_verses, f, ensure_ascii=False, indent=2)
        
        return len(verses), len(modified_verses)
    
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return 0, 0

def main():
    """Main function to run the verse cleaning pipeline."""
    # Setup directories
    input_dir = "output_files"
    output_dir = "processed_verses"
    modified_dir = "modified_verses"
    
    # Create output directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(modified_dir, exist_ok=True)
    
    print("\n📋 Sanskrit Verse Cleaning Pipeline")
    print("----------------------------------")
    
    # Get all input files
    input_files = glob.glob(os.path.join(input_dir, "output-*.json"))
    if not input_files:
        print(f"No JSON files found in '{input_dir}'")
        return
    
    # Sort files by batch number
    input_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
    
    # Print first file contents for debugging
    print(f"\nChecking first file contents:")
    with open(input_files[0], 'r', encoding='utf-8') as f:
        first_file = json.load(f)
        print(f"Number of verses in first file: {len(first_file)}")
        print(f"Sample verse: {first_file[0]['verse']}")
    
    total_verses = 0
    total_modified = 0
    
    # Process each batch file with progress bar
    for input_file in tqdm(input_files, desc="Processing batches"):
        verses_count, modified_count = process_batch(input_file, output_dir, modified_dir)
        total_verses += verses_count
        total_modified += modified_count
    
    print("\n🎉 Verse Cleaning Pipeline completed!")
    print(f"📊 Total verses processed: {total_verses}")
    print(f"✏️ Total verses modified: {total_modified}")
    
    # Report output sizes
    def get_dir_size(dir_path):
        total = 0
        for file in glob.glob(os.path.join(dir_path, "*.json")):
            total += os.path.getsize(file)
        return total / 1024  # Size in KB
    
    processed_size = get_dir_size(output_dir)
    modified_size = get_dir_size(modified_dir)
    
    print(f"\n📁 Processed verses directory size: {processed_size:.2f} KB")
    print(f"📁 Modified verses directory size: {modified_size:.2f} KB")

if __name__ == "__main__":
    main() 