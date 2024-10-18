-- Create a stored procedure to compute average weighted score for users
DROP PROCEDURE IF EXISTS ComputeAverageWeightedScoreForUsers;

DELIMITER //

CREATE PROCEDURE ComputeAverageWeightedScoreForUsers()
BEGIN
    -- Declare variables
    DECLARE done INT DEFAULT 0;
    DECLARE current_user_id INT;
    DECLARE weighted_sum FLOAT;
    DECLARE total_weight INT;
    DECLARE cur CURSOR FOR 
        SELECT id FROM users;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open cursor
    OPEN cur;

    read_loop: LOOP
        -- Fetch the user id
        FETCH cur INTO current_user_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate weighted sum and total weight for the current user
        SELECT SUM(c.score * p.weight), SUM(p.weight)
        INTO weighted_sum, total_weight
        FROM corrections c
        JOIN projects p ON c.project_id = p.id
        WHERE c.user_id = current_user_id;

        -- Update the average score in users table if total_weight is greater than 0
        IF total_weight > 0 THEN
            UPDATE users
            SET average_score = weighted_sum / total_weight
            WHERE id = current_user_id;
        ELSE
            -- If no projects found, set average_score to 0
            UPDATE users
            SET average_score = 0
            WHERE id = current_user_id;
        END IF;

    END LOOP;

    -- Close cursor
    CLOSE cur;
END //

DELIMITER ;
