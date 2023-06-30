CREATE TRIGGER increment_total_jobs
    AFTER INSERT
    ON jobs
    FOR EACH ROW
BEGIN
    UPDATE servers
    SET total_jobs = total_jobs + 1
    WHERE id = NEW.server_id;
END;



