from bs4 import BeautifulSoup
from pydantic import BaseModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


def process_all_html(input_dir, output_dir):
    if not input_dir.exists():
        logging.warning(f"Input directory not found: {input_dir}")
        return

    process_count = 0
    skip_count = 0    
    output_dir.mkdir(parents=True, exist_ok=True)
    for html_file in input_dir.glob("*.html"):
        try:
            with open(html_file, "r", encoding="utf-8") as in_file:
                soup = BeautifulSoup(in_file, "html.parser")
                source_id = (
                    soup.find("meta", property="og:url")["content"]
                    .rstrip("/").split("/")[-1]
                )
                job_title = get_soup_text(soup, "job-detail-title")
                if not job_title:
                    logging.warning(f"Missing job title in: {html_file.name}")
                    skip_count += 1
                    continue
                company = get_soup_text(soup, "advertiser-name")
                if not company:
                    logging.warning(f"Missing company in: {html_file.name}")
                    skip_count += 1
                    continue
                description = get_soup_text(soup, "jobAdDetails")
                if not description:
                    logging.warning(f"Missing description in: {html_file.name}")
                    skip_count += 1
                    continue
        except Exception as code:
            logging.error(f"Error processing {html_file.name}: {code}")
            skip_count += 1
            continue

        output_data = JobListing(
            source_id = source_id,
            job_title = job_title,
            company = company,
            description = description
        )
        if generate_json_success(output_dir, html_file, output_data):
            process_count += 1
        else:
            skip_count += 1

    total_count = len(list(input_dir.glob("*.html")))
    print(f"\n📊 Silver Summary:\nTotal: {total_count} | "
          f"Processed: {process_count} | Skipped: {skip_count}")


def get_soup_text(soup, attr_value):    
    tag = soup.find(attrs={"data-automation": attr_value})
    if tag is None:
        return None
    if attr_value == "jobAdDetails":
        return " ".join(tag.get_text(separator=" ", strip=True).split())
    return tag.get_text(separator=" ", strip=True)


def generate_json_success(output_dir, html_file, output_data):    
    output_path = output_dir / (html_file.stem + ".json")
    try:
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(output_data.model_dump_json(indent=2))
            logging.info(f"Processed: {html_file.name}")
            return True
    except Exception as code:
        logging.error(f"Error writing JSON for {html_file.name}: {code}")
        return False