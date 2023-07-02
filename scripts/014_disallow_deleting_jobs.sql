CREATE TRIGGER forbid_delete_jobs
BEFORE DELETE ON jobs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Deleting from the jobs table is forbidden.';
END;