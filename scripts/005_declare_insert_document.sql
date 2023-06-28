-- Function to insert a document and create a server if not exists
CREATE FUNCTION insert_document(url VARCHAR(750), server VARCHAR(128), title TEXT, body LONGTEXT, title_tokens LONGTEXT,
                                body_tokens LONGTEXT, all_harvested_links TEXT, relevant_links TEXT, relevant BOOLEAN)
    RETURNS INT
    DETERMINISTIC
BEGIN
    DECLARE job_id INT;
    DECLARE job_done BOOLEAN;

    -- Check if the job exists
    SELECT id, done INTO job_id, job_done FROM job WHERE url = url;

    IF job_id IS NULL THEN
        -- Job does not exist, insert job first using insert_job function
        SET job_id = insert_job(url, server, 0);
        SET job_done = FALSE;
    ELSE
        -- Job exists, check if it is done
        IF job_done THEN
            -- Job is done, raise an error or handle it accordingly
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Job is already done';
        ELSE
            -- Job is not done, proceed with inserting the document
            INSERT INTO document (url, server_id, title, body, title_tokens, body_tokens, all_harvested_links,
                                  relevant_links, relevant)
            VALUES (url, (SELECT server_id FROM job WHERE id = job_id), title, body, title_tokens, body_tokens,
                    all_harvested_links, relevant_links, relevant);
        END IF;
    END IF;

    RETURN LAST_INSERT_ID();
END