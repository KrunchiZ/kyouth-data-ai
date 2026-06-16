import os
import re
import sqlite3
import logging
from pathlib import Path

QUERY_DIR = Path("queries")
COUNT_JOBS_QUERY = QUERY_DIR / "count_jobs.sql"
COUNT_NULL_TITLES_QUERY = QUERY_DIR / "count_null_titles.sql"
COUNT_NULL_COMPANIES_QUERY = QUERY_DIR / "count_null_companies.sql"
COUNT_NULL_DESC_QUERY = QUERY_DIR / "count_null_descriptions.sql"
COUNT_AVG_DESC_LENGTH_QUERY = QUERY_DIR / "count_avg_desc_length.sql"
COUNT_SHORTEST_DESC_QUERY = QUERY_DIR / "count_shortest_desc.sql"
COUNT_LONGEST_DESC_QUERY = QUERY_DIR / "count_longest_desc.sql"
SET_QUALITY_QUERY = QUERY_DIR / "set_quality.sql"
QUARANTINE_PROFILES_QUERY = QUERY_DIR / "quarantine_profiles.sql"
GET_LOW_PROFILES_QUERY = QUERY_DIR / "get_low_profiles.sql"
DELETE_LOW_PROFILES_QUERY = QUERY_DIR / "delete_low_profiles.sql"


logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_data_profile(db_path):
	if not input_db_isValid(db_path):
		return
	stats = get_data_profile_stats(db_path)
	if stats is not None:
		print_data_profile_report(stats)
		set_data_quality(db_path)
		quarantine_profiles(db_path)


def input_db_isValid(db_path):
	if not os.path.isfile(db_path):
		logging.error(f"Database not found: {db_path}")
		return False
	if not os.access(db_path, os.R_OK):
		logging.error(f"Database not readable: {db_path}")
		return False
	return True


def get_data_profile_stats(db_path):
	stats = {
		"total_records":0,
		"null_titles": 0,
		"null_companies": 0,
		"null_descriptions": 0,
		"avg_length": 0,
		"shortest_desc": (None, None, None),
		"longest_desc": (None, None, None)
	}
	try:
		with sqlite3.connect(db_path) as conn:
			cursor = conn.cursor()
			cursor.execute(COUNT_JOBS_QUERY.read_text(encoding="utf-8"))
			stats["total_records"] = cursor.fetchone()[0]
			cursor.execute(COUNT_NULL_TITLES_QUERY.read_text(encoding="utf-8"))
			stats["null_titles"] = cursor.fetchone()[0]
			cursor.execute(COUNT_NULL_COMPANIES_QUERY.read_text(encoding="utf-8"))
			stats["null_companies"] = cursor.fetchone()[0]
			cursor.execute(COUNT_NULL_DESC_QUERY.read_text(encoding="utf-8"))
			stats["null_descriptions"] = cursor.fetchone()[0]
			cursor.execute(COUNT_AVG_DESC_LENGTH_QUERY.read_text(encoding="utf-8"))
			stats["avg_length"] = cursor.fetchone()[0]
			cursor.execute(COUNT_SHORTEST_DESC_QUERY.read_text(encoding="utf-8"))
			stats["shortest_desc"] = cursor.fetchone()
			cursor.execute(COUNT_LONGEST_DESC_QUERY.read_text(encoding="utf-8"))
			stats["longest_desc"] = cursor.fetchone()
	except sqlite3.Error as code:
		logging.error(f"Profile Error: {code}")
		return None
	return stats


def print_data_profile_report(stats):
	print(
		f"--- 🔍 DATA QUALITY REPORT ---"
		f"\n📊 Total Records: {stats['total_records']}"
		f"\n❓ Missing Values -> job_title: {stats['null_titles']}, "
		f"company: {stats['null_companies']}, "
		f"description: {stats['null_descriptions']}"
		f"\n📝 Avg Description Length: {stats['avg_length']} chars"
		f"\n⚠️ Shortest Description: {stats['shortest_desc'][2]} chars"
		f"\n    ↳ source_id: {stats['shortest_desc'][0]} | "
		f"job_title: {stats['shortest_desc'][1]}"
		f"\n🚨 Longest Description: {stats['longest_desc'][2]} chars"
		f"\n    ↳ source_id: {stats['longest_desc'][0]} | "
		f"job_title: {stats['longest_desc'][1]}"
	)


def set_data_quality(db_path):
	def has_consecutive_special(pattern, value):
		return bool(re.search(pattern, value)) if value else False

	try:
		with sqlite3.connect(db_path) as conn:
			cursor = conn.cursor()
			conn.create_function("REGEXP", 2, has_consecutive_special)
			cursor.executescript(SET_QUALITY_QUERY.read_text(encoding="utf-8"))
	except sqlite3.Error as code:
		logging.error(f"Set Quality Error: {code}")


def quarantine_profiles(db_path):
	try:
		with sqlite3.connect(db_path) as conn:
			cursor = conn.cursor()
			cursor.executescript(
				QUARANTINE_PROFILES_QUERY.read_text(encoding="utf-8"))
			cursor.execute(GET_LOW_PROFILES_QUERY.read_text(encoding="utf-8"))
			low_profiles = cursor.fetchall()
			cursor.execute(
				DELETE_LOW_PROFILES_QUERY.read_text(encoding="utf-8"))
			print(f"❌ Quarantined {cursor.rowcount} low quality profiles.")
			for profile in low_profiles:
				print(f"    ↳ source_id: {profile[0]} | job_title: {profile[1]}")
	except sqlite3.Error as code:
		logging.error(f"Quarantine Error: {code}")
