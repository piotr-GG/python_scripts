# Flashcards XML to CSV Processor

This script processes flashcard data stored in XML files, extracts key fields, and outputs the data to CSV files. It also includes translation functionality, using Google Translate, to translate Italian sentences into Polish.

## Features

- **XML Parsing**: Extracts `original`, `sentence (Italian)`, and `translation` fields from flashcard XML files.
- **CSV Generation**: Produces CSV files with the extracted data.
- **Duplicate Removal**: Identifies and removes duplicate entries based on the Italian sentence.
- **Translation**: Uses Google Translate to translate Italian sentences into Polish and merges the original, Italian, and Polish sentences into the final CSV file.

## Requirements

- Python 3.x
- Packages:
  - `pandas`
  - `googletrans`
  - `xml.etree.ElementTree`
  - `csv`
  - `pathlib`
  - `os`

To install required dependencies, run:

```bash
pip install pandas googletrans==4.0.0-rc1
