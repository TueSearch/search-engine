CREATE TRIGGER forbid_delete_documents
    BEFORE DELETE
    ON documents
    FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Deleting from the documents table is forbidden.';
END;