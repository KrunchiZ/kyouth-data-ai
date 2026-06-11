UPDATE jobs
SET job_title       = ?,
    company         = ?,
    description     = ?,
    tech_stack      = ?,
    quality         = ?,
    content_hash    = ?
WHERE source_id = ?;