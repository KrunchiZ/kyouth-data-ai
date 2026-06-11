UPDATE jobs
SET quality = 'LOW'
WHERE 
    job_title IS NULL 
    OR company IS NULL 
    OR description IS NULL
    OR LENGTH(description) < 100
    OR description REGEXP '[!#@\*\$%\?]{4,}';

UPDATE jobs
SET quality = 'HIGH'
WHERE
    quality IS NULL;