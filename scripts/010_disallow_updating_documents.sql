CREATE TRIGGER forbid_update_documents
BEFORE UPDATE ON documents
FOR EACH ROW
BEGIN
    IF NEW.title != OLD.title OR
       NEW.meta_description != OLD.meta_description OR
       NEW.meta_keywords != OLD.meta_keywords OR
       NEW.meta_author != OLD.meta_author OR
       NEW.h1 != OLD.h1 OR
       NEW.h2 != OLD.h2 OR
       NEW.h3 != OLD.h3 OR
       NEW.h4 != OLD.h4 OR
       NEW.h5 != OLD.h5 OR
       NEW.h6 != OLD.h6 OR
       NEW.body != OLD.body OR
       NEW.created_date != OLD.created_date
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Updates on title, meta_description, meta_keywords, meta_author, h1, h2, h3, h4, h5, h6, body and created_date fields are forbidden.';
    END IF;
END