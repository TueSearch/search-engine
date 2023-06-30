CREATE TRIGGER increment_success_jobs
    AFTER UPDATE
    ON jobs
    FOR EACH ROW
BEGIN
    IF NEW.success = TRUE THEN -- Only an approximation, but good enough.
    UPDATE servers
    SET success_jobs = success_jobs + 1
    WHERE id = NEW.server_id;
END IF;
END;