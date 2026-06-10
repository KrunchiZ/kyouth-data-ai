from hashlib import sha256
import json
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

def load_all_jsons(input_dir, output_dir):
    # load_all_jsons Function — Responsibilities
    # 1. Read all .json files from the Silver input directory
    # 2. Ensure data/3_gold/ directory exists (create if missing)
    # 3. Connect to jobs.db and create the jobs table if it doesn't exist
    # 4. For each file, attempt INSERT OR IGNORE with the relevant fields
    # 5. Check cursor.rowcount to determine inserted vs skipped
    # 6. Print status for each record
    # 7. Commit the transaction and close the connection
    if not input_dir.exists():
        logging.warning(f"⚠ Input directory not found: {input_dir}")
        return
    
    insert_count = 0
    skip_count = 0    
    output_dir.mkdir(parents=True, exist_ok=True)
    conn = init_db(output_dir / "jobs.db")
    cursor = conn.cursor()
    for json_file in input_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as in_file:
                data = json.load(in_file)

            source_id = data["source_id"]
            job_title = data["job_title"]
            company = data["company"]
            description = data["description"]
            hash_input = f"{job_title}|{company}|{description}"
            content_hash = sha256(hash_input.encode()).hexdigest()

            record = {    
                "source_id": source_id,
                "job_title": job_title,
                "company": company,
                "description": description,
                "tech_stack": None,
                "quality": None,
                "content_hash": content_hash
            }
            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    source_id, job_title, company, description,
                    tech_stack, quality, content_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, 
                tuple(record.values())
            )
            if cursor.rowcount == 1:
                logging.info(f"Inserted: {json_file.name}")
                insert_count += 1
            else:
                logging.warning(f"⚠ Skipped (duplicate): {json_file.name}")
                skip_count += 1
            conn.commit()

        except Exception as code:
            logging.error(f"⚠ Skipped ({code}): {json_file.name}")
            skip_count += 1
            continue
    
    total_count = len(list(input_dir.glob("*.json")))
    print(f"\n📊 Gold Summary:\nTotal: {total_count} | "
          f"Inserted: {insert_count} | Skipped: {skip_count}")


def init_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                source_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT NOT NULL,
                tech_stack TEXT,
                quality TEXT,
                content_hash TEXT NOT NULL
            )
            """
        )
    conn.commit()
    return conn