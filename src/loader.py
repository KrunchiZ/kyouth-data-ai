import os
import json
import sqlite3
import logging
from pathlib import Path
from hashlib import sha256


logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(message)s"
)

QUERY_DIR = Path("queries")
OPEN_TABLE_QUERY = QUERY_DIR / "open_table.sql"
INSERT_FIELDS_QUERY = QUERY_DIR / "insert_fields.sql"
GET_CONTENT_HASH_QUERY = QUERY_DIR / "get_content_hash.sql"


def load_all_jsons(input_dir, output_dir):
	if not input_dir_isValid(input_dir):
		return
	if not init_output_dir(output_dir):
		return

	insert_count = 0
	conn = init_db(output_dir / "jobs.db")
	cursor = conn.cursor()
	for json_file in input_dir.glob("*.json"):
		try:
			with open(json_file, "r", encoding="utf-8") as in_file:
				data = json.load(in_file)
			
			entry = init_entry(data)
			cursor.execute(GET_CONTENT_HASH_QUERY.read_text(encoding="utf-8")
							, (entry["source_id"],))
			existing_hash = cursor.fetchone()
			if (existing_hash is not None 
				and existing_hash[0] == entry["content_hash"]):
				logging.info(f"Skipped (duplicate): {json_file.name}")
				continue
			upsert_entry(conn, entry)
			if existing_hash is None:
				logging.info(f"Inserted: {json_file.name}")
			else:
				logging.info(f"Updated: {json_file.name}")
			insert_count += 1
			conn.commit()

		except Exception as code:
			logging.error(f"Skipped ({code}): {json_file.name}")
			continue        

	conn.close()
	total_count = len(list(input_dir.glob("*.json")))
	print(f"\n📊 Gold Summary:\nTotal: {total_count} | "
		  f"Inserted: {insert_count} | Skipped: {total_count - insert_count}")


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


def init_db(db_path):
	with sqlite3.connect(db_path) as conn:
		cursor = conn.cursor()
		cursor.execute(OPEN_TABLE_QUERY.read_text(encoding="utf-8"))
	return conn


def init_entry(data):
	# Create a unique hash for the job posting based on its content.
	# Exclude source_id, tech_stack and quality.
	hash_input = f"{data['job_title']}|{data['company']}|{data['description']}"

	return {    
		"source_id":    data["source_id"],
		"job_title":    data["job_title"],
		"company":      data["company"],
		"description":  data["description"],
		"tech_stack":   None,
		"quality":      None,
		"content_hash": sha256(hash_input.encode()).hexdigest()
	}


def upsert_entry(conn, entry):
	cursor = conn.cursor()
	cursor.execute(INSERT_FIELDS_QUERY.read_text(encoding="utf-8"), (
					entry["source_id"],
					entry["job_title"],
					entry["company"],
					entry["description"],
					entry["tech_stack"],
					entry["quality"],
					entry["content_hash"]
	))