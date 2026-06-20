from dataclasses import Field
import os
import logging
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError, Field

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(message)s"
)

class JobListing(BaseModel):
	source_id   : str = Field(min_length=1)
	job_title   : str = Field(min_length=1)
	company     : str = Field(min_length=1)
	description : str = Field(min_length=1)


def process_all_html(input_dir, output_dir):
	if not input_dir_isValid(input_dir):
		return
	if not init_output_dir(output_dir):
		return    

	process_count = 0
	for html_file in input_dir.glob("*.html"):
		try:
			with open(html_file, "r", encoding="utf-8") as in_file:
				soup = BeautifulSoup(in_file, "html.parser")
				source_id = (soup.find("meta", property="og:url")["content"]
							.rstrip("/").split("/")[-1])
				job_title = get_soup_text(soup, "job-detail-title")
				company = get_soup_text(soup, "advertiser-name")
				description = get_soup_text(soup, "jobAdDetails")
		except Exception as code:
			logging.error(f"Error processing {html_file.name}: {code}")
			continue

		try:
			output_data = JobListing(
				source_id = source_id,
				job_title = job_title,
				company = company,
				description = description
			)
			output_path = output_dir / (html_file.stem + ".json")
			with open(output_path, "w", encoding="utf-8") as out_file:
				out_file.write(output_data.model_dump_json(indent=2))
				logging.info(f"Processed: {html_file.name}")
				process_count += 1

		except ValidationError as code:
			for error in code.errors():
				logging.error(f"Missing {error['loc'][0].strip()} "
							  f"in {html_file.name}")
		except Exception as code:
			logging.error(f"{code}: {html_file.name}")

	total_count = len(list(input_dir.glob("*.html")))
	print(f"\n📊 Silver Summary:\nTotal: {total_count} | Processed: "
		  f"{process_count} | Skipped: {total_count - process_count}")


def input_dir_isValid(input_dir):
	if not input_dir.exists():
		logging.warning(f"Input directory not found: {input_dir}")
		return False
	if not os.access(input_dir, os.R_OK):
		logging.warning(f"Input directory not readable: {input_dir}")
		return False
	return True


def init_output_dir(output_dir):
	try:
		output_dir.mkdir(parents=True, exist_ok=True)
		return True
	except Exception as code:
		logging.error(f"{code}: {output_dir}")
		return False


def get_soup_text(soup, attr_value):    
	tag = soup.find(attrs={"data-automation": attr_value})
	if tag is None:
		return None
	if attr_value == "jobAdDetails":
		return "\n".join(
			" ".join(tag.get_text(separator="\n", strip=True)
			.split(" ")).splitlines()
		)
	return tag.get_text(separator=" ", strip=True)