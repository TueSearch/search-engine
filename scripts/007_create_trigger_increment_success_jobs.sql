CREATE TRIGGER increment_success_jobs
    BEFORE UPDATE
    ON jobs
    FOR EACH ROW
BEGIN
    IF NEW.done != OLD.done THEN
        IF NEW.success = TRUE THEN -- Only an approximation, but good enough.
            UPDATE servers
            SET success_jobs = success_jobs + 1
            WHERE id = NEW.server_id;
        END IF;
        UPDATE servers
        set total_done_jobs = total_done_jobs + 1
        WHERE id = NEW.server_id;
    END IF;
END;