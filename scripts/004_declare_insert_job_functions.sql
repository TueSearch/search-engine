-- Function to insert a job and create a server if not exists
CREATE FUNCTION insert_job(url VARCHAR(1024), server_name VARCHAR(128), priority INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE server_id INT;
    DECLARE is_blacklist INT;
    
    -- Check if the server exists
    SELECT id, is_black_list INTO server_id, is_blacklist FROM server WHERE name = server_name;
    
    -- If server does not exist, create it
    IF server_id IS NULL THEN
        INSERT INTO server (name) VALUES (server_name);
        SET server_id = LAST_INSERT_ID();
    ELSEIF is_blacklist = 1 THEN
        -- Server exists and is blacklisted, do not add the job
        RETURN 0;
    END IF;
    
    -- Insert the job
    INSERT INTO job (url, server_id, priority)
    VALUES (url, server_id, priority);
    
    RETURN LAST_INSERT_ID();
END