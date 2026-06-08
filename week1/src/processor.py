from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError

def process_all_html(input_dir, output_dir):
    # Process all HTML files in the input_dir
    # Strip HTML tags, derive source_id from metadata, clean the text
    # Validate the cleaned text with pydantic
    # Save the results to output_dir in .json format