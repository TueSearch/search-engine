CREATE TRIGGER forbid_update_servers
BEFORE UPDATE ON servers
FOR EACH ROW
BEGIN
    IF NEW.id != OLD.id OR
       NEW.name != OLD.name OR
       NEW.created_date != OLD.created_date
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Updates on id, name, and created_date fields are forbidden.';
    END IF;
END