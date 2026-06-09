import logging
import json
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError


logging.basicConfig(level=logging.INFO, format="%(message)s")

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


def process_all_html(input_dir, output_dir):
    # Process all HTML files in the input_dir
    # Strip HTML tags, derive source_id from metadata, clean the text
    # Validate the cleaned text with pydantic
    # Save the results to output_dir in .json format

    if not input_dir.exists():
        logging.warning(f"⚠️ Input directory not found: {input_dir}")
        return

    process_count = 0
    skip_count = 0    
    output_dir.mkdir(parents=True, exist_ok=True)
    for html_file in input_dir.glob("*.html"):
        with open(html_file, "r", encoding="utf-8") as in_file:
            soup = BeautifulSoup(in_file, "html.parser")
            source_id = (
                soup.find("meta", property="og:url")["content"]
                .rstrip("/").split("/")[-1]
            )
    
    total_count = len(list(input_dir.glob("*.html")))
    logging.info(f"\n📊 Silver Summary:\nTotal: {total_count} "
                 f"| Processed: {process_count} | Skipped: {skip_count}")