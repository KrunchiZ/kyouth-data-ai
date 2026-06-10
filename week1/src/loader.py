import json
import sqlite3
import logging
from hashlib import sha256

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(levelname)s |%(message)s"
)

def load_all_jsons(input_dir, output_dir):
    if not input_dir.exists():
        logging.warning(f"⚠ Input directory not found: {input_dir}")
        return
    
    insert_count = 0
    skip_count = 0    
    output_dir.mkdir(parents=True, exist_ok=True)
    conn = init_db(output_dir / "jobs.db")
    for json_file in input_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as in_file:
                data = json.load(in_file)
            
            entry = init_entry(data)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO jobs (
                        source_id, job_title, company, description,
                        tech_stack, quality, content_hash
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, 
                    tuple(entry.values())
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

    conn.close()
    total_count = len(list(input_dir.glob("*.json")))
    print(f"\n📊 Gold Summary:\nTotal: {total_count} | "
          f"Inserted: {insert_count} | Skipped: {skip_count}")


def init_db(db_path):
    with sqlite3.connect(db_path) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    source_id       TEXT PRIMARY KEY,
                    job_title       TEXT NOT NULL,
                    company         TEXT NOT NULL,
                    description     TEXT NOT NULL,
                    tech_stack      TEXT,
                    quality         TEXT,
                    content_hash    TEXT NOT NULL
                )
                """
            )
    conn.commit()
    return conn


def init_entry(data):
    source_id =     data["source_id"]
    job_title =     data["job_title"]
    company =       data["company"]
    description =   data["description"]
    hash_input =    f"{job_title}|{company}|{description}"
    content_hash =  sha256(hash_input.encode()).hexdigest()    

    return {    
        "source_id":    source_id,
        "job_title":    job_title,
        "company":      company,
        "description":  description,
        "tech_stack":   None,
        "quality":      None,
        "content_hash": content_hash
    }