CREATE TRIGGER increment_relevant_documents
AFTER INSERT ON documents
FOR EACH ROW
BEGIN
    IF NEW.relevant = TRUE THEN
        UPDATE servers
        SET relevant_documents = relevant_documents + 1
        WHERE id = (
            SELECT server_id
            FROM jobs
            WHERE jobs.id = NEW.job_id
        );
    END IF;
END