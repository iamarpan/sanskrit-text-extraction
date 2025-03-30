import os
import json
import re

# Mapping of Hindi numerals to English numerals
hindi_to_english = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"
}

# Mapping of English names to Hindi names
english_to_hindi = {
    "ashvalayana_grihya_sutra": "अश्वलयन ग्रिह्य सुत्र",
    "ashvalayana_shrauta_sutra":"अश्वलयन श्रौत सुत्र",
    "Baudhayana_shrauta_sutra":"बौधयन श्रौत सुत्र",
    "Baudhayana_Shulba_Sutra":"बौधयन शुल्ब सुत्र",
    "gautama_dharma_sutra":"गौतम धर्म सुत्र",
    "vasishtha_dharma_sutra":"वसिश्थ धर्म सुत्र",
    "drahyayana_grihya_sutra":"द्रह्ययन ग्रिह्य सुत्र",
    "gobhila_grihya_sutra":"गोभिल ग्रिह्य सुत्र",
    "hiranyakeshi_grihya_sutra":"हिरन्यकेशि ग्रिह्य सुत्र",
    "kathaka_grihya_sutra":"कथक ग्रिह्य सुत्र",
    "kaushitaka_grihya_sutra":"कौशितक ग्रिह्य सुत्र",
    "vadhula_grihya_sutra":"वधुल ग्रिह्य सुत्र",
    "varaha_grihya_sutra":"वरह ग्रिह्य सुत्र",
    "sUryasiddhAntaH_pAThAntaropetaH":"सूर्यसिद्धान्तः पाठान्तरोपेतः",
    "vivAhapaTala":"विवाहपटल",
    "yogayAtrA":"योगयात्रा",
    "yogayAtrA_Pingree_edition.md":"योगयात्रा पिन्ग्री",
    "lagadha_vedanga_jyotish":"लगध वेदन्ग ज्योतिश्",
    "AngIrasa-smRtiH":"अन्गिरसस्म्रितिह्",
    "brihaspati-smRtiH":"ब्रिहस्पतिस्म्र्तिह्",
    "devala-smRtiH":"देवलस्म्र्तिह्",
    "naradeyadharmashartam":"नरदेयधर्मशर्तम्",
    "vashishtha_smriti":"वशिश्थस्म्रिति",
    "vishwamitra_smriti":"विश्वमित्रस्म्रिति",
    "yogadeepika":"योगदीपिका"
}

def replace_hindi_numerals(text):
    """Replace Hindi numerals with English numerals in the given text."""
    return re.sub(r'[०-९]', lambda x: hindi_to_english[x.group()], text)

def replace_english_name(text):
    """Replace the English filename at the start of 'ref' with the corresponding Hindi name."""
    parts = text.split("->", 1)
    if parts[0] in english_to_hindi:
        parts[0] = english_to_hindi[parts[0]]
    return "->".join(parts)

def process_json_file(file_path):
    """Process a JSON file and update Hindi numerals and names in the 'ref' key."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Update the 'ref' field for each object in the JSON array
        for obj in data:
            if 'ref' in obj:
                obj['ref'] = replace_hindi_numerals(obj['ref'])
                obj['ref'] = replace_english_name(obj['ref'])

        # Write the updated data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def traverse_and_process(directory):
    """Recursively traverse directories and process 'output.json' files."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "output.json":
                file_path = os.path.join(root, file)
                process_json_file(file_path)

# Replace 'your_directory_path' with the actual root directory containing nested folders
traverse_and_process("/Users/arpansrivastava/Development/BHERI-scrapper/sanskrit-text-extraction")


