import json
import os
import glob

def combine_json_files(input_dir="output_files", output_file="output.json"):
    """
    Combines all JSON files from the input directory into a single output file.
    Replaces dots with arrows in the ref field of each verse.
    
    Args:
        input_dir (str): Directory containing the JSON files to combine
        output_file (str): Name of the output file
    """
    print(f"\n--- Combining JSON files from '{input_dir}' ---")
    
    # Get all JSON files in the input directory
    json_files = glob.glob(os.path.join(input_dir, "output-*.json"))
    if not json_files:
        print(f"No JSON files found in '{input_dir}'")
        return
    
    # Sort files by batch number
    json_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
    print(f"Found {len(json_files)} JSON files to combine")
    
    # Combine all verses
    all_verses = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                verses = json.load(f)
                # Replace dots with arrows in ref field
                for verse in verses:
                    verse['ref'] = verse['ref'].replace('.', '->')
                all_verses.extend(verses)
                print(f"Added {len(verses)} verses from {os.path.basename(json_file)}")
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue
    
    # Write combined verses to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_verses, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully combined {len(all_verses)} verses into {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    input_dir = "processed_verses"  # Directory containing batch JSON files
    output_file = "output.json"  # Name of the combined output file
    
    combine_json_files(input_dir, output_file) 