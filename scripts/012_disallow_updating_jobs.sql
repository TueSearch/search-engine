CREATE TRIGGER forbid_update_jobs
BEFORE UPDATE ON jobs
FOR EACH ROW
BEGIN
    IF NEW.id != OLD.id OR
       NEW.url != OLD.url OR
       NEW.server_id != OLD.server_id OR
       NEW.parent_id != OLD.parent_id OR
       NEW.anchor_text != OLD.anchor_text OR
       NEW.anchor_text_tokens != OLD.anchor_text_tokens OR
       NEW.surrounding_text != OLD.surrounding_text OR
       NEW.surrounding_text_tokens != OLD.surrounding_text_tokens OR
       NEW.title_text != OLD.title_text OR
       NEW.title_text_tokens != OLD.title_text_tokens OR
       NEW.created_date != OLD.created_date
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Updates on id, url, server_id, parent_id, anchor_text, anchor_text_tokens, surrounding_text, surrounding_text_tokens, title_text, title_text_tokens, and created_date fields are forbidden.';
    END IF;
END