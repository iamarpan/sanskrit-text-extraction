#!/usr/bin/env python3
import os
import subprocess
import sys
import time

def run_script(script_name, description):
    """
    Runs a Python script and handles its execution.
    
    Args:
        script_name (str): The name of the script to run.
        description (str): Description of what the script does.
    
    Returns:
        bool: True if the script executed successfully, False otherwise.
    """
    print(f"\n{'=' * 50}")
    print(f"RUNNING: {description}")
    print(f"{'=' * 50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully.")
            return True
        else:
            print(f"\n❌ {script_name} failed with return code {result.returncode}.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {script_name} failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False

def main():
    """
    Main function to run the Sanskrit text scraping pipeline.
    """
    start_time = time.time()
    
    print("\n📋 Sanskrit Text Extraction Pipeline")
    print("-----------------------------------")
    
    # Step 1: Scrape URLs
    if not run_script("scrape_urls.py", "Scraping URLs from the source website"):
        print("Pipeline stopped due to URL scraping failure.")
        return
    
    # Step 2: Filter URLs
    if not run_script("filter_urls.py", "Filtering URLs that contain Sanskrit verses"):
        print("Pipeline stopped due to URL filtering failure.")
        return
    
    # Step 3: Extract content from URLs
    if not run_script("scrape_content.py", "Extracting Sanskrit verses from filtered URLs"):
        print("Pipeline stopped due to content extraction failure.")
        return
    
    # Calculate total execution time
    end_time = time.time()
    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    
    print("\n🎉 Complete Sanskrit Text Extraction Pipeline finished successfully!")
    print(f"⏱️ Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds")
    
    # Check if output file exists and report its size
    output_file = "extracted_verses.json"
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024  # Size in KB
        if file_size < 1024:
            print(f"📄 Output file size: {file_size:.2f} KB")
        else:
            print(f"📄 Output file size: {file_size/1024:.2f} MB")
    
if __name__ == "__main__":
    main() 