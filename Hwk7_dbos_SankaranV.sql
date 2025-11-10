USE harry_potter_book_v2025;

-- ============================================================================
-- Question 1: Function num_spells_with_type(spell_type_p)
-- Returns the number of spells with the given spell type
-- ============================================================================

DROP FUNCTION IF EXISTS num_spells_with_type;

DELIMITER $$

CREATE FUNCTION num_spells_with_type(spell_type_p VARCHAR(255))
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE spell_count INT;
    
    -- Count spells with the given spell_type
    SELECT COUNT(*) INTO spell_count
    FROM spell
    WHERE spell_type = spell_type_p;
    
    RETURN spell_count;
END$$

DELIMITER ;

-- Test cases for Question 1
SELECT num_spells_with_type('Hex') AS spell_count;
SELECT num_spells_with_type('Charm') AS spell_count;
SELECT num_spells_with_type('Curse') AS spell_count;
SELECT num_spells_with_type('Jinx') AS spell_count;

-- ============================================================================
-- Question 2: Procedure get_role_in_book(book_number_p)
-- Returns all role names and book title for a given book number
-- ============================================================================

DROP PROCEDURE IF EXISTS get_role_in_book;

DELIMITER $$

CREATE PROCEDURE get_role_in_book(IN book_number_p INT)
BEGIN
    SELECT 
        rt.name AS character_name,
        b.title AS book_title
    FROM role_trimmed rt
    INNER JOIN role_in_book rib ON rt.id = rib.role_id
    INNER JOIN book b ON rib.book_id = b.book_number
    WHERE b.book_number = book_number_p
    ORDER BY b.title ASC, rt.name ASC;
END$$

DELIMITER ;

-- Test cases for Question 2
CALL get_role_in_book(1);
CALL get_role_in_book(2);
CALL get_role_in_book(7);

-- ============================================================================
-- Question 3: Procedure get_spell_instance_details(spell_name_p)
-- Returns role id, role name, spell name, spell type
-- NOTE: role_to_spell table does NOT have book_id, so book info cannot be included
-- ============================================================================

DROP PROCEDURE IF EXISTS get_spell_instance_details;

DELIMITER $$

CREATE PROCEDURE get_spell_instance_details(IN spell_name_p VARCHAR(255))
BEGIN
    SELECT DISTINCT
        rt.id AS role_id,
        rt.name AS role_name,
        s.name AS spell_name,
        s.spell_type,
        'N/A - not in schema' AS book_title
    FROM role_trimmed rt
    INNER JOIN role_to_spell rts ON rt.id = rts.role_id
    INNER JOIN spell s ON rts.spell_id = s.id
    WHERE s.name = spell_name_p
    ORDER BY rt.name ASC, s.name ASC;
END$$

DELIMITER ;

-- Test cases for Question 3
CALL get_spell_instance_details('Accio');
CALL get_spell_instance_details('Stupefy');
CALL get_spell_instance_details('Lumos');

-- ============================================================================
-- Question 4: Function more_books(role1_p, role2_p)
-- Compares the number of books two roles have appeared in
-- Returns: 1 if role1 > role2, 0 if equal, -1 if role1 < role2
-- ============================================================================

DROP FUNCTION IF EXISTS more_books;

DELIMITER $$

CREATE FUNCTION more_books(role1_p VARCHAR(255), role2_p VARCHAR(255))
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE role1_count INT DEFAULT 0;
    DECLARE role2_count INT DEFAULT 0;
    DECLARE role1_exists INT DEFAULT 0;
    DECLARE role2_exists INT DEFAULT 0;
    
    -- Check if role1 exists
    SELECT COUNT(*) INTO role1_exists
    FROM role_trimmed
    WHERE name = role1_p;
    
    -- Check if role2 exists
    SELECT COUNT(*) INTO role2_exists
    FROM role_trimmed
    WHERE name = role2_p;
    
    -- Signal error if either role doesn't exist
    IF role1_exists = 0 OR role2_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'One or both role names not found in role_trimmed table';
    END IF;
    
    -- Get book count for role1
    SELECT COUNT(DISTINCT rib.book_id) INTO role1_count
    FROM role_trimmed rt
    INNER JOIN role_in_book rib ON rt.id = rib.role_id
    WHERE rt.name = role1_p;
    
    -- Get book count for role2
    SELECT COUNT(DISTINCT rib.book_id) INTO role2_count
    FROM role_trimmed rt
    INNER JOIN role_in_book rib ON rt.id = rib.role_id
    WHERE rt.name = role2_p;
    
    -- Return comparison result
    IF role1_count > role2_count THEN
        RETURN 1;
    ELSEIF role1_count = role2_count THEN
        RETURN 0;
    ELSE
        RETURN -1;
    END IF;
END$$

DELIMITER ;

-- Test cases for Question 4
SELECT more_books('Harry Potter', 'Hermione Granger') AS comparison;
SELECT more_books('Albus Dumbledore', 'Draco Malfoy') AS comparison;
SELECT more_books('Severus Snape', 'Albus Dumbledore') AS comparison;

-- Test error handling
-- SELECT more_books('Invalid Name', 'Harry Potter') AS comparison; -- Should throw error

-- ============================================================================
-- Question 5: Procedure get_house_affiliation(house_name_p)
-- Returns roles affiliated with a house with confidence levels
-- NOTE: Column name is 'house' not 'house_name' in role_trimmed table
-- ============================================================================

DROP PROCEDURE IF EXISTS get_house_affiliation;

DELIMITER $$

CREATE PROCEDURE get_house_affiliation(IN house_name_p VARCHAR(255))
BEGIN
    DECLARE valid_house INT DEFAULT 0;
    
    -- Check if house name is one of the four valid houses
    -- Note: Using 'Hufflepuff' not 'HufflePuff' as per assignment, but schema has 'Hufflepuff'
    IF house_name_p IN ('Gryffindor', 'Ravenclaw', 'Hufflepuff', 'Slytherin') THEN
        SET valid_house = 1;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid house name. Must be Gryffindor, Ravenclaw, Hufflepuff, or Slytherin';
    END IF;
    
    -- Return results with confidence levels
    SELECT 
        rt.id AS role_id,
        rt.name AS role_name,
        rt.gender,
        rt.eye_color,
        rt.hair_color,
        CASE
            WHEN rt.house = house_name_p THEN 'Definitely'
            WHEN rt.house LIKE '%likely%' AND rt.house LIKE CONCAT('%', house_name_p, '%') THEN 'Highly likely'
            WHEN rt.house LIKE '%possibly%' AND rt.house LIKE CONCAT('%', house_name_p, '%') THEN 'Possibly'
            WHEN rt.house IN ('Gryffindor', 'Ravenclaw', 'Hufflepuff', 'Slytherin') 
                 AND rt.house != house_name_p THEN 'Possibly'
            ELSE 'Possibly'
        END AS confidence_level
    FROM role_trimmed rt
    WHERE rt.house = house_name_p
       OR rt.house LIKE CONCAT('%', house_name_p, '%')
    ORDER BY 
        CASE 
            WHEN rt.house = house_name_p THEN 1
            WHEN rt.house LIKE '%likely%' THEN 2
            ELSE 3
        END,
        rt.name ASC;
END$$

DELIMITER ;

-- Test cases for Question 5
CALL get_house_affiliation('Gryffindor');
CALL get_house_affiliation('Slytherin');
CALL get_house_affiliation('Ravenclaw');
CALL get_house_affiliation('Hufflepuff');

-- Test error handling
-- CALL get_house_affiliation('InvalidHouse'); -- Should throw error

-- ============================================================================
-- Question 6: Alter role_trimmed table and create set_num_spell_count procedure
-- Adds num_spells field and initializes it for a specific role
-- ============================================================================

-- Alter table (execute only once)
-- Check if column exists before adding
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'role_trimmed' 
AND COLUMN_NAME = 'num_spells';

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE role_trimmed ADD COLUMN num_spells INT DEFAULT 0',
    'SELECT ''Column num_spells already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

DROP PROCEDURE IF EXISTS set_num_spell_count;

DELIMITER $$

CREATE PROCEDURE set_num_spell_count(IN role_p VARCHAR(255))
BEGIN
    DECLARE role_exists INT DEFAULT 0;
    DECLARE spell_count INT DEFAULT 0;
    DECLARE role_id_var INT;
    
    -- Check if role exists and get role_id
    SELECT COUNT(*), MAX(id) INTO role_exists, role_id_var
    FROM role_trimmed
    WHERE name = role_p;
    
    IF role_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Role name not found in role_trimmed table';
    END IF;
    
    -- Count spells for the role
    SELECT COUNT(*) INTO spell_count
    FROM role_to_spell rts
    WHERE rts.role_id = role_id_var;
    
    -- Update the num_spells field
    UPDATE role_trimmed
    SET num_spells = spell_count
    WHERE id = role_id_var;
    
    SELECT CONCAT('Updated num_spells for ', role_p, ' to ', spell_count) AS result;
END$$

DELIMITER ;

-- Test cases for Question 6
CALL set_num_spell_count('Albus Dumbledore');
CALL set_num_spell_count('Hermione Granger');
CALL set_num_spell_count('Severus Snape');

-- Verify updates
SELECT name, num_spells 
FROM role_trimmed 
WHERE name IN ('Albus Dumbledore', 'Hermione Granger', 'Severus Snape');

-- Test error handling
-- CALL set_num_spell_count('Invalid Name'); -- Should throw error

-- ============================================================================
-- Question 7: Procedure update_all_roles_num_spells()
-- Updates num_spells for all roles using cursor
-- ============================================================================

DROP PROCEDURE IF EXISTS update_all_roles_num_spells;

DELIMITER $$

CREATE PROCEDURE update_all_roles_num_spells()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE current_role_name VARCHAR(255);
    DECLARE roles_updated INT DEFAULT 0;
    
    -- Declare cursor
    DECLARE role_cursor CURSOR FOR 
        SELECT name FROM role_trimmed;
    
    -- Declare handler
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Open cursor
    OPEN role_cursor;
    
    -- Loop through all roles
    read_loop: LOOP
        FETCH role_cursor INTO current_role_name;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Call the procedure from question 6 (suppress output)
        CALL set_num_spell_count(current_role_name);
        SET roles_updated = roles_updated + 1;
    END LOOP;
    
    -- Close cursor
    CLOSE role_cursor;
    
    SELECT CONCAT('Updated num_spells for ', roles_updated, ' roles') AS result;
END$$

DELIMITER ;

-- Test case for Question 7
CALL update_all_roles_num_spells();

-- Verify all updates
SELECT name, num_spells 
FROM role_trimmed 
WHERE num_spells > 0
ORDER BY num_spells DESC 
LIMIT 20;

-- ============================================================================
-- Question 8: Trigger spell_cnt_update_after_role_to_spell_insert
-- Updates num_spells when a new spell is added to role_to_spell
-- ============================================================================

DROP TRIGGER IF EXISTS spell_cnt_update_after_role_to_spell_insert;

DELIMITER $$

CREATE TRIGGER spell_cnt_update_after_role_to_spell_insert
AFTER INSERT ON role_to_spell
FOR EACH ROW
BEGIN
    DECLARE current_spell_count INT;
    
    -- Count total spells for this role
    SELECT COUNT(*) INTO current_spell_count
    FROM role_to_spell
    WHERE role_id = NEW.role_id;
    
    -- Update the num_spells field
    UPDATE role_trimmed
    SET num_spells = current_spell_count
    WHERE id = NEW.role_id;
END$$

DELIMITER ;

-- Test cases for Question 8

-- First, get the role_id and spell_id
SELECT @test_role_id := id 
FROM role_trimmed 
WHERE name = 'Draco Malfoy' 
LIMIT 1;

SELECT @test_spell_id := id 
FROM spell 
WHERE name = 'Accio' 
LIMIT 1;

-- Check current num_spells
SELECT name, num_spells 
FROM role_trimmed 
WHERE id = @test_role_id;

-- Insert a new spell instance (NOTE: no book_id in role_to_spell)
INSERT INTO role_to_spell (role_id, spell_id)
VALUES (@test_role_id, @test_spell_id);

-- Verify the trigger updated num_spells
SELECT name, num_spells 
FROM role_trimmed 
WHERE id = @test_role_id;

-- Test case 2: Another character and spell
SELECT @test_role_id2 := id 
FROM role_trimmed 
WHERE name = 'Minerva McGonagall' 
LIMIT 1;

SELECT @test_spell_id2 := id 
FROM spell 
WHERE name = 'Lumos' 
LIMIT 1;

-- Check current count
SELECT name, num_spells 
FROM role_trimmed 
WHERE id = @test_role_id2;

-- Insert new spell instance
INSERT INTO role_to_spell (role_id, spell_id)
VALUES (@test_role_id2, @test_spell_id2);

-- Verify trigger worked
SELECT name, num_spells 
FROM role_trimmed 
WHERE id = @test_role_id2;

-- ============================================================================
-- Question 9: Prepared Statement for num_spells_with_type function
-- Uses user session variable to pass spell type
-- ============================================================================

-- Test case 1: Hex
SET @spell_type_var = 'Hex';
PREPARE stmt FROM 'SELECT num_spells_with_type(?) AS spell_count';
EXECUTE stmt USING @spell_type_var;
DEALLOCATE PREPARE stmt;

-- Test case 2: Charm
SET @spell_type_var = 'Charm';
PREPARE stmt FROM 'SELECT num_spells_with_type(?) AS spell_count';
EXECUTE stmt USING @spell_type_var;
DEALLOCATE PREPARE stmt;

-- Test case 3: Curse
SET @spell_type_var = 'Curse';
PREPARE stmt FROM 'SELECT num_spells_with_type(?) AS spell_count';
EXECUTE stmt USING @spell_type_var;
DEALLOCATE PREPARE stmt;

-- Test case 4: Jinx
SET @spell_type_var = 'Jinx';
PREPARE stmt FROM 'SELECT num_spells_with_type(?) AS spell_count';
EXECUTE stmt USING @spell_type_var;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- Additional Procedure for Part 2 (Question 16)
-- Procedure spell_has_type(type_p) for the application
-- ============================================================================

DROP PROCEDURE IF EXISTS spell_has_type;

DELIMITER $$

CREATE PROCEDURE spell_has_type(IN type_p VARCHAR(255))
BEGIN
    DECLARE type_exists INT DEFAULT 0;
    
    -- Check if spell type exists
    SELECT COUNT(*) INTO type_exists
    FROM spell_type
    WHERE type_name = type_p;
    
    IF type_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'The passed spell type is not valid';
    END IF;
    
    -- Return spells with this type
    SELECT 
        s.id AS spell_id,
        s.name AS spell_name,
        s.alias AS spell_alias
    FROM spell s
    WHERE s.spell_type = type_p
    ORDER BY s.name ASC;
END$$

DELIMITER ;

-- Test cases for spell_has_type
CALL spell_has_type('Hex');
CALL spell_has_type('Charm');
CALL spell_has_type('Curse');

-- Test error handling
-- CALL spell_has_type('InvalidType'); -- Should throw error

-- ============================================================================
-- END OF SQL FILE
-- ============================================================================