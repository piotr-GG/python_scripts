import os
import pathlib
import xml.etree.ElementTree as ET
import pandas as pd
import csv

from googletrans import Translator

# Input and output CSV file paths
INPUT_DIR = './flashcards_input'
PREPROCESSED_CSV = 'preprocessed_cards.csv'
CLEANED_CSV = 'cleaned_cards.csv'
OUTPUT_CSV = 'output.csv'

# Open CSV file for writing (without translation)
with open(PREPROCESSED_CSV, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write CSV header
    writer.writerow(['Original', 'Translation', 'Sentence (Italian)'])

    # Process each XML file
    for xml_file in pathlib.Path(os.getcwd(), INPUT_DIR).iterdir():
        if xml_file.suffix != '.xml':
            continue

        print(f"Processing {xml_file}...")
        file_path = os.path.join(INPUT_DIR, xml_file)

        # Parse XML data
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Loop through each card in the XML
            for card in root.findall(".//card"):
                original = card.find(".//rich-text[@name='original']").text or ''
                sentence_it = card.find(".//rich-text[@name='sentence']").text or ''
                translation = card.find(".//rich-text[@name='translation']").text or ''

                # Write row to CSV
                writer.writerow([original, sentence_it, translation])

        except ET.ParseError as e:
            print(f"Error parsing {xml_file}: {e}")
        except FileNotFoundError as e:
            print(f"File {xml_file} not found: {e}")

print(f"CSV file '{PREPROCESSED_CSV}' created successfully.")

# PANDAS part
# Read the original CSV into a DataFrame and count duplicates based on the 'Sentence (Italian)' column
df = pd.read_csv(PREPROCESSED_CSV)
duplicate_count = df.duplicated(subset=['Sentence (Italian)'], keep=False).sum()
print(f"Found {duplicate_count} duplicates.")

# Remove duplicates and save the cleaned data
df_unique = df.drop_duplicates(subset=['Sentence (Italian)'])
df_unique.to_csv(CLEANED_CSV, index=False)
print(f"Duplicates removed and data saved to 'cleaned_cards.csv'.")

# Initialize Google Translate (unofficial)
translator = Translator()

count = 0
# Open the cleaned CSV for reading and the translated CSV for writing
with open(CLEANED_CSV, mode='r', newline='', encoding='utf-8') as input_csv:
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as output_csv:
        reader = csv.reader(input_csv)
        writer = csv.writer(output_csv, quoting=csv.QUOTE_MINIMAL, delimiter=';')

        # Read header from the original file but do not write it to the new file (drop it)
        header = next(reader)

        # Translate each sentence and write it to the new CSV
        for row in reader:
            original, sentence_it, translation = row

            # Skip empty sentences
            if sentence_it:
                try:
                    # Translate the sentence
                    sentence_pl = translator.translate(sentence_it, src='it', dest='pl').text
                    count += 1
                    print(f"#{count} Translated '{sentence_it}' to '{sentence_pl}'")
                except Exception as e:
                    print(f"Error translating sentence '{sentence_it}': {e}")
                    sentence_pl = ''
            else:
                sentence_pl = ''

            # Merge the original and translated sentences into one column
            first_column = original
            # Merge the column and add newlines between the fields
            merged_column = f"{translation}\n{sentence_it}\n{sentence_pl}"
            writer.writerow([first_column, merged_column])
print(f"CSV file '{OUTPUT_CSV}' created successfully with translated sentences.")
