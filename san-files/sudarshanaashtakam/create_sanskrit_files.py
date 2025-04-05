import os
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re
import sys

def create_sudarshana_ashtakam():
    content = """॥ श्री सुदर्शनाष्टकम् ॥

॥ श्रीः ॥
श्रीमते रामानुजाय नमः
श्रीमते निगमान्तमहादेशिकाय नमः

१. प्रतिभटश्रेणिभीषण वरगुणस्तोमभूषण
   जनिभयस्थानतारण जगदवस्थानकारण
   निखिलदुष्कर्मकर्शन निगमसद्धर्मदर्शन
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

२. शुभजगद्रूपमण्डन सुरगणत्रासखण्डन
   शतमखब्रह्मवन्दित शतपथब्रह्मनन्दित
   प्रथितविद्वत्सपक्षित भजदहिर्बुध्न्यलक्षित
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

३. स्फुटतटिज्जालपिञ्जर पृथुतरज्वालपञ्जर
   परिगतप्रत्नविग्रह पटुतरप्रज्ञदुर्ग्रह
   प्रहरणग्राममण्डित परिजनत्राणपण्डित
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

४. निजपदप्रीतसद्गण निरुपधिस्फीतषड्गुण
   निगमनिर्व्यूढवैभव निजपरव्यूहवैभव
   हरिहयद्वेषिदारण हरपुरप्लोषकारण
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

५. दनुजविस्तारकर्तन जनितमिस्राविकर्तन
   दनुजविद्यानिकर्तन भजदविद्यानिवर्तन
   अमरदृष्टस्वविक्रम समरजुष्टभ्रमिक्रम
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

६. प्रतिमुखालीढबन्धुर पृथुमहाहेतिदन्तुर
   विकटमायाबहिष्कृत विविधमालापरिष्कृत
   स्थिरमहायन्त्रतन्त्रित दृढदयातन्त्रयन्त्रित
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

७. महितसम्पत्सदक्षर विहितसम्पत्षडक्षर
   षडरचक्रप्रतिष्ठित सकलतत्त्वप्रतिष्ठित
   विविधसङ्कल्पकल्पक विबुधसङ्कल्पकल्पक
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

८. भुवननेत्रत्रयीमय सवनतेजस्त्रयीमय
   निरवधिस्वादुचिन्मय निखिलशक्ते जगन्मय
   अमितविश्वक्रियामय शमितविष्वग्भयामय
   जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन

फलश्रुति:
द्विचतुष्कमिदं प्रभूतसारं पठतां वेङ्कटनायकप्रणीतम् ।
विषमेऽपि मनोरथः प्रधावन् न विहन्येत रथाङ्गधूर्यगुप्तः ॥

॥ इति श्री सुदर्शनाष्टकं समाप्तम् ॥"""
    return content

def create_raghuveera_gadyam():
    content = """श्री महावीरवैभवम्
(श्री रघुवीरगद्यम्)

॥ श्रीः ॥
श्रीमते रामानुजाय नमः
श्रीमते निगमान्तमहादेशिकाय नमः

बालकाण्डम्
जय जय महावीर
महाधीर धौरेय
देवासुर समर समय समुदित निखिल निर्जर निर्धारित निरवधिक माहात्म्य
दशवदन दमित दैवत परिषदभ्यर्थित दाशरथि भाव
दिनकर कुल कमल दिवाकर

अयोध्याकाण्डम्
अनृत भय मुषित हृदय पितृ वचन पालन प्रतिज्ञावज्ञात यौवराज्य
निषाद राज सौहृद सूचित सौशील्य सागर
भरद्वाज शासन परिगृहीत विचित्र चित्रकूट गिरि कटक तट रम्यावसथ

आरण्यकाण्डम्
दण्डका तपोवन
विराध हरिण
विलुठित बहुफल मख कलम रजनिचर मृग
त्रिशिरः शिरस्त्रितय
दूषण जलनिधि शोषण तोषित ऋषिगण

किष्किन्धाकाण्डम्
प्रभञ्जन तनय भावुक
तरणिसुत शरणागति
दृढघटित कैलास कोटि विकट दुन्दुभि कङ्काड
अतिपृथुल बहु विटपि गिरि धरणि विवर

सुन्दरकाण्डम्
अपार पारावार परिखा परिवृत परपुर परिसृत दव

युद्धकाण्डम्
अहित सहोदर रक्षः परिग्रह विसंवादि विविध
सकृत् प्रपन्न जन
वीर
सत्यव्रत

उत्तरकाण्डम्
[कथा समाप्ति]

॥ इति श्री रघुवीरगद्यं समाप्तम् ॥"""
    return content

def create_achyuta_shatakam():
    content = """॥ श्री अच्युतशतकम् ॥

॥ श्रीः ॥
श्रीमते रामानुजाय नमः
श्रीमते निगमान्तमहादेशिकाय नमः

१. नमः त्रिदशान नाथं
   सत्यं दासानामच्युतं स्थिरज्योतिः
   गरुडनदीतटतमालम्
   अहीन्द्रनगरौषधाचलैकगजेन्द्रम्

२. किङ्करसत्य स्तुतिस्तव
   स्वयंभूगेहिनीविलासव्याहृतमयी
   फणिता बालेन मया
   पञ्जरशुकजल्पितमिव करोतु प्रसादम्

[... remaining verses ...]

॥ इति श्री अच्युतशतकं समाप्तम् ॥"""
    return content

def convert_san_to_devanagari(input_file, output_file):
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Sanskrit text portions (text within \san{...} commands)
        sanskrit_portions = re.findall(r'\\san(?:\[[\d\.]+\])?\s*{([^}]+)}', content)
        
        converted_text = []
        
        for portion in sanskrit_portions:
            # Remove LaTeX formatting and quotes
            clean_text = portion.strip().strip('"')
            
            # Convert to IAST (intermediate step)
            iast_text = clean_text.replace('aa', 'ā')\
                                 .replace('ii', 'ī')\
                                 .replace('uu', 'ū')\
                                 .replace('"s', 'ś')\
                                 .replace('.t', 'ṭ')\
                                 .replace('.d', 'ḍ')\
                                 .replace('.n', 'ṇ')\
                                 .replace('.r', 'ṛ')\
                                 .replace('.m', 'ṃ')\
                                 .replace('.h', 'ḥ')\
                                 .replace('~n', 'ñ')\
                                 .replace('.l', 'ḷ')
            
            # Convert to Devanagari
            devanagari = transliterate(iast_text, sanscript.IAST, sanscript.DEVANAGARI)
            converted_text.append(devanagari)
        
        # Join the converted text with newlines
        final_text = '\n'.join(converted_text)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_text)
            
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find the input file {input_file}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py input.san [output.txt]")
        print("If output file is not specified, will create input_converted.txt")
        return
    
    input_file = sys.argv[1]
    
    # If output file is not specified, create default name
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = input_file.rsplit('.', 1)[0] + '_converted.txt'
    
    # Install required package if not present
    try:
        import indic_transliteration
    except ImportError:
        print("Installing required package 'indic-transliteration'...")
        import pip
        pip.main(['install', 'indic-transliteration'])
        print("Package installed successfully!")
    
    convert_san_to_devanagari(input_file, output_file)

if __name__ == "__main__":
    main()
