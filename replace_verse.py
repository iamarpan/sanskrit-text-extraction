import os

def replace_in_file(file_path, old_text, new_text):
    """Replaces occurrences of old_text with new_text in the given file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = content.replace(old_text, new_text)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

def process_folder(parent_folder, old_text="verse_number", new_text="ref"):
    """Recursively processes all output.json files in the given folder."""
    for root, _, files in os.walk(parent_folder):
        for file in files:
            if file == "output.json":
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                replace_in_file(file_path, old_text, new_text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <parent_folder>")
    else:
        parent_folder = sys.argv[1]
        process_folder(parent_folder)

