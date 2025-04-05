from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re
import os

def convert_san_to_devanagari(input_file, output_file):
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Initialize converted text with title and invocation
        converted_text = """॥ श्री अच्युतशतकम् ॥

॥ श्रीः ॥
श्रीमते रामानुजाय नमः
श्रीमते निगमान्तमहादेशिकाय नमः

"""
        
        # Track verses we've processed
        processed_verses = set()
        
        # Extract Sanskrit verses with their numbers - using a more flexible pattern
        verse_pattern = r'{\\sana\s+([^}]+)}[^{]*{\\sdds{(\d+)}'
        verses = re.findall(verse_pattern, content)
        
        # Process verses in numerical order
        sorted_verses = sorted(verses, key=lambda x: int(x[1]))
        for verse_text, verse_num in sorted_verses:
            # Skip if we've already processed this verse number
            if verse_num in processed_verses:
                continue
                
            processed_verses.add(verse_num)
            
            # Clean and convert the Sanskrit verse
            clean_text = verse_text.strip().replace('\\\\', '\n').replace('\\', '')
            
            # Remove all curly braces and their contents
            clean_text = re.sub(r'{[^}]*}', '', clean_text)
            
            # Fix special characters in preprocessing
            clean_text = clean_text.replace('"s', 'ś')
            clean_text = clean_text.replace('".s', 'ṣ')
            clean_text = clean_text.replace('.t', 'ṭ')
            clean_text = clean_text.replace('.d', 'ḍ')
            clean_text = clean_text.replace('.n', 'ṇ')
            clean_text = clean_text.replace('.r', 'ṛ')
            clean_text = clean_text.replace('.m', 'ṃ')
            clean_text = clean_text.replace('.h', 'ḥ')
            clean_text = clean_text.replace('~n', 'ñ')
            clean_text = clean_text.replace('j~n', 'jñ')
            clean_text = clean_text.replace('.l', 'ḷ')
            clean_text = clean_text.replace('aa', 'ā')
            clean_text = clean_text.replace('ii', 'ī')
            clean_text = clean_text.replace('uu', 'ū')
            clean_text = clean_text.replace(';', '')
            clean_text = clean_text.replace('"', '')
            clean_text = clean_text.replace('.', '')
            
            # Remove any remaining special characters or markers
            clean_text = re.sub(r'[{}]', '', clean_text)
            clean_text = re.sub(r'sd$', '', clean_text)
            
            # Split into lines and process each line
            lines = clean_text.split('\n')
            clean_lines = []
            for line in lines:
                if line.strip():
                    # Additional cleanup
                    line = line.strip()
                    line = re.sub(r'\s+', ' ', line)  # normalize whitespace
                    clean_lines.append(line)
            
            # Convert to Devanagari
            devanagari_lines = []
            for line in clean_lines:
                try:
                    # Convert any remaining problematic characters
                    line = line.replace('।', '.')
                    line = re.sub(r'[\[\]{}]', '', line)
                    
                    devanagari = transliterate(line, sanscript.IAST, sanscript.DEVANAGARI)
                    
                    # Final cleanup of Devanagari text
                    devanagari = re.sub(r'[%]', '', devanagari)
                    devanagari = re.sub(r'स्द्', '', devanagari)
                    devanagari = re.sub(r'।', '', devanagari)
                    devanagari = re.sub(r'"', '', devanagari)
                    devanagari = re.sub(r'\.', '', devanagari)
                    
                    devanagari_lines.append(devanagari)
                except Exception as e:
                    print(f"Error converting line: {line}")
                    # Keep original but cleaned
                    clean_line = re.sub(r'[{}]', '', line)
                    devanagari_lines.append(clean_line)
            
            # Format verse with number and proper indentation
            formatted_verse = f"{verse_num}. " + "\n   ".join(devanagari_lines) + "\n\n"
            converted_text += formatted_verse
        
        # Add closing
        converted_text += "\n॥ इति श्री अच्युतशतकं समाप्तम् ॥"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_text)
            
        print(f"Successfully converted {input_file} to {output_file} with {len(processed_verses)} verses")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

# Convert the file
input_file = 'accuasaam/accuasaam.san'
output_file = 'accuasaam/achyuta_shatakam.txt'

convert_san_to_devanagari(input_file, output_file) 