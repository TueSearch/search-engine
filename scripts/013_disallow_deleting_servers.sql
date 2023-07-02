CREATE TRIGGER forbid_delete_servers
    BEFORE DELETE
    ON servers
    FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Deleting from the servers table is forbidden.';
END;