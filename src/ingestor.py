import os
import quopri
import logging
from email import message_from_binary_file

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(message)s"
)

def ingest_all_mhtml(input_dir, output_dir):
	if not input_dir_isValid(input_dir):
		return
	if not init_output_dir(output_dir):
		return    
		
	extract_count = 0   
	for mhtml_file in input_dir.glob("*.mhtml"):
		extract_count = ingest_mhtml(extract_count, mhtml_file, output_dir)
	
	total_count = len(list(input_dir.glob("*.mhtml")))
	print(
		f"\n📊 Bronze Summary:\nTotal: {total_count} | "
		f"Extracted: {extract_count} | Failed: {total_count - extract_count}"
	)


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


def ingest_mhtml(extract_count, mhtml_file, output_dir):
	try:
		with open(mhtml_file, "rb") as in_file:
			html_found = False
			msg = message_from_binary_file(in_file)
			for part in msg.walk():    
				if part.get_content_type() == "text/html":
					html_found = True
					charset = part.get_content_charset() or "utf-8"
					html_str = part.get_payload()
					if not html_str:
						logging.warning(f"Empty HTML content in: {mhtml_file.name}")
						break
					if isinstance(html_str, str):
						html_str = quopri.decodestring(html_str.encode())
					html_str = html_str.decode(charset, errors="replace")

					output_path = output_dir / (mhtml_file.stem + ".html")
					if write_html(output_path, html_str, mhtml_file):
						extract_count += 1
					break
			if not html_found:
				logging.warning(f"No HTML content found in: {mhtml_file.name}")

	except Exception as code:
		logging.error(f"Error ingesting {mhtml_file.name}: {code}")

	return extract_count


def write_html(output_path, html_str, mhtml_file):
	try:
		with open(output_path, "w", encoding="utf-8") as out_file:
			out_file.write(html_str)
			logging.info(f"Extracted: {mhtml_file.name}")
			return True
	except Exception as code:
		logging.error(f"Error writing HTML: {mhtml_file.name}: {code}")
		return False