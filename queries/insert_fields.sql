INSERT OR IGNORE INTO jobs (
    source_id, job_title, company, description,
    tech_stack, quality, content_hash
)
VALUES (?, ?, ?, ?, ?, ?, ?);