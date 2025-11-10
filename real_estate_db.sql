-- =====================================================
-- Real Estate Database Management System
-- MySQL Schema with Tables, Procedures, Functions, Triggers
-- Group of 2 - 10 Tables
-- =====================================================

DROP DATABASE IF EXISTS real_estate_db;
CREATE DATABASE real_estate_db;
USE real_estate_db;

-- =====================================================
-- TABLE DEFINITIONS
-- =====================================================

-- Table 1: Users (Base table for all system users)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('admin', 'agent', 'client') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB;

-- Table 2: Locations
CREATE TABLE Locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    street_address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    country VARCHAR(50) DEFAULT 'USA',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    INDEX idx_city (city),
    INDEX idx_zip (zip_code),
    INDEX idx_coordinates (latitude, longitude)
) ENGINE=InnoDB;

-- Table 3: PropertyTypes
CREATE TABLE PropertyTypes (
    property_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    INDEX idx_type_name (type_name)
) ENGINE=InnoDB;

-- Table 4: Agents
CREATE TABLE Agents (
    agent_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    agency_name VARCHAR(100),
    commission_rate DECIMAL(5, 2) DEFAULT 3.00,
    specialization VARCHAR(100),
    years_experience INT DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    total_sales INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK (commission_rate >= 0 AND commission_rate <= 100),
    CHECK (rating >= 0 AND rating <= 5),
    INDEX idx_license (license_number),
    INDEX idx_rating (rating)
) ENGINE=InnoDB;

-- Table 5: Clients
CREATE TABLE Clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    preferred_contact_method ENUM('email', 'phone', 'text') DEFAULT 'email',
    budget_min DECIMAL(12, 2),
    budget_max DECIMAL(12, 2),
    preferred_location VARCHAR(100),
    looking_for ENUM('buy', 'rent', 'sell') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK (budget_max >= budget_min),
    INDEX idx_budget (budget_min, budget_max)
) ENGINE=InnoDB;

-- Table 6: Properties
CREATE TABLE Properties (
    property_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    property_type_id INT NOT NULL,
    agent_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(12, 2) NOT NULL,
    listing_type ENUM('sale', 'rent') NOT NULL,
    bedrooms INT NOT NULL DEFAULT 0,
    bathrooms DECIMAL(3, 1) NOT NULL DEFAULT 0,
    square_feet INT,
    lot_size DECIMAL(10, 2),
    year_built INT,
    status ENUM('available', 'pending', 'sold', 'rented', 'off_market') DEFAULT 'available',
    listed_date DATE NOT NULL,
    sold_date DATE,
    parking_spaces INT DEFAULT 0,
    has_garage BOOLEAN DEFAULT FALSE,
    has_pool BOOLEAN DEFAULT FALSE,
    has_garden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (property_type_id) REFERENCES PropertyTypes(property_type_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES Agents(agent_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CHECK (price > 0),
    CHECK (bedrooms >= 0),
    CHECK (bathrooms >= 0),
    CHECK (year_built >= 1800 AND year_built <= 2024),
    INDEX idx_price (price),
    INDEX idx_status (status),
    INDEX idx_listing_type (listing_type),
    INDEX idx_location (location_id),
    INDEX idx_agent (agent_id)
) ENGINE=InnoDB;

-- Table 7: PropertyImages
CREATE TABLE PropertyImages (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    caption VARCHAR(200),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES Properties(property_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    INDEX idx_property (property_id),
    INDEX idx_primary (is_primary)
) ENGINE=InnoDB;

-- Table 8: Appointments
CREATE TABLE Appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    client_id INT NOT NULL,
    agent_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES Properties(property_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES Agents(agent_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK (duration_minutes > 0),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_status (status),
    INDEX idx_property (property_id),
    INDEX idx_client (client_id),
    INDEX idx_agent (agent_id)
) ENGINE=InnoDB;

-- Table 9: Transactions
CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    client_id INT NOT NULL,
    agent_id INT NOT NULL,
    transaction_type ENUM('sale', 'rental') NOT NULL,
    transaction_date DATE NOT NULL,
    final_price DECIMAL(12, 2) NOT NULL,
    commission_amount DECIMAL(12, 2),
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    lease_start_date DATE,
    lease_end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES Properties(property_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES Agents(agent_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CHECK (final_price > 0),
    CHECK (commission_amount >= 0),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_payment_status (payment_status),
    INDEX idx_property (property_id),
    INDEX idx_client (client_id),
    INDEX idx_agent (agent_id)
) ENGINE=InnoDB;

-- Table 10: Reviews
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    property_id INT,
    agent_id INT,
    rating INT NOT NULL,
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (property_id) REFERENCES Properties(property_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES Agents(agent_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    CHECK (rating >= 1 AND rating <= 5),
    INDEX idx_rating (rating),
    INDEX idx_property (property_id),
    INDEX idx_agent (agent_id)
) ENGINE=InnoDB;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure 1: Create a new property listing
DELIMITER //
CREATE PROCEDURE sp_create_property(
    IN p_location_id INT,
    IN p_property_type_id INT,
    IN p_agent_id INT,
    IN p_title VARCHAR(200),
    IN p_description TEXT,
    IN p_price DECIMAL(12,2),
    IN p_listing_type ENUM('sale', 'rent'),
    IN p_bedrooms INT,
    IN p_bathrooms DECIMAL(3,1),
    IN p_square_feet INT,
    OUT p_property_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_property_id = -1;
    END;
    
    START TRANSACTION;
    
    INSERT INTO Properties (
        location_id, property_type_id, agent_id, title, description,
        price, listing_type, bedrooms, bathrooms, square_feet,
        listed_date, status
    ) VALUES (
        p_location_id, p_property_type_id, p_agent_id, p_title, p_description,
        p_price, p_listing_type, p_bedrooms, p_bathrooms, p_square_feet,
        CURDATE(), 'available'
    );
    
    SET p_property_id = LAST_INSERT_ID();
    COMMIT;
END//
DELIMITER ;

-- Procedure 2: Schedule an appointment
DELIMITER //
CREATE PROCEDURE sp_schedule_appointment(
    IN p_property_id INT,
    IN p_client_id INT,
    IN p_agent_id INT,
    IN p_appointment_date DATETIME,
    IN p_notes TEXT,
    OUT p_appointment_id INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE property_status VARCHAR(20);
    DECLARE conflict_count INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_appointment_id = -1;
        SET p_message = 'Error scheduling appointment';
    END;
    
    START TRANSACTION;
    
    -- Check if property is available
    SELECT status INTO property_status 
    FROM Properties 
    WHERE property_id = p_property_id;
    
    IF property_status != 'available' THEN
        SET p_appointment_id = -1;
        SET p_message = 'Property is not available for viewing';
        ROLLBACK;
    ELSE
        -- Check for scheduling conflicts
        SELECT COUNT(*) INTO conflict_count
        FROM Appointments
        WHERE agent_id = p_agent_id
        AND status = 'scheduled'
        AND ABS(TIMESTAMPDIFF(MINUTE, appointment_date, p_appointment_date)) < 60;
        
        IF conflict_count > 0 THEN
            SET p_appointment_id = -1;
            SET p_message = 'Agent has a scheduling conflict';
            ROLLBACK;
        ELSE
            INSERT INTO Appointments (
                property_id, client_id, agent_id, appointment_date, notes
            ) VALUES (
                p_property_id, p_client_id, p_agent_id, p_appointment_date, p_notes
            );
            
            SET p_appointment_id = LAST_INSERT_ID();
            SET p_message = 'Appointment scheduled successfully';
            COMMIT;
        END IF;
    END IF;
END//
DELIMITER ;

-- Procedure 3: Complete a transaction
DELIMITER //
CREATE PROCEDURE sp_complete_transaction(
    IN p_property_id INT,
    IN p_client_id INT,
    IN p_transaction_type ENUM('sale', 'rental'),
    IN p_final_price DECIMAL(12,2),
    OUT p_transaction_id INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_agent_id INT;
    DECLARE v_commission_rate DECIMAL(5,2);
    DECLARE v_commission_amount DECIMAL(12,2);
    DECLARE v_new_status VARCHAR(20);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_transaction_id = -1;
        SET p_message = 'Transaction failed';
    END;
    
    START TRANSACTION;
    
    -- Get agent and commission rate
    SELECT p.agent_id, a.commission_rate 
    INTO v_agent_id, v_commission_rate
    FROM Properties p
    JOIN Agents a ON p.agent_id = a.agent_id
    WHERE p.property_id = p_property_id;
    
    -- Calculate commission
    SET v_commission_amount = p_final_price * (v_commission_rate / 100);
    
    -- Set new property status
    IF p_transaction_type = 'sale' THEN
        SET v_new_status = 'sold';
    ELSE
        SET v_new_status = 'rented';
    END IF;
    
    -- Create transaction
    INSERT INTO Transactions (
        property_id, client_id, agent_id, transaction_type,
        transaction_date, final_price, commission_amount, payment_status
    ) VALUES (
        p_property_id, p_client_id, v_agent_id, p_transaction_type,
        CURDATE(), p_final_price, v_commission_amount, 'completed'
    );
    
    SET p_transaction_id = LAST_INSERT_ID();
    
    -- Update property status
    UPDATE Properties 
    SET status = v_new_status, sold_date = CURDATE()
    WHERE property_id = p_property_id;
    
    -- Update agent total sales
    UPDATE Agents 
    SET total_sales = total_sales + 1
    WHERE agent_id = v_agent_id;
    
    SET p_message = 'Transaction completed successfully';
    COMMIT;
END//
DELIMITER ;

-- =====================================================
-- USER DEFINED FUNCTIONS
-- =====================================================

-- Function 1: Calculate property price per square foot
DELIMITER //
CREATE FUNCTION fn_price_per_sqft(p_property_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_price DECIMAL(12,2);
    DECLARE v_sqft INT;
    DECLARE v_price_per_sqft DECIMAL(10,2);
    
    SELECT price, square_feet INTO v_price, v_sqft
    FROM Properties
    WHERE property_id = p_property_id;
    
    IF v_sqft > 0 THEN
        SET v_price_per_sqft = v_price / v_sqft;
    ELSE
        SET v_price_per_sqft = 0;
    END IF;
    
    RETURN v_price_per_sqft;
END//
DELIMITER ;

-- Function 2: Get agent's total commission earned
DELIMITER //
CREATE FUNCTION fn_agent_total_commission(p_agent_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total_commission DECIMAL(12,2);
    
    SELECT COALESCE(SUM(commission_amount), 0) INTO v_total_commission
    FROM Transactions
    WHERE agent_id = p_agent_id AND payment_status = 'completed';
    
    RETURN v_total_commission;
END//
DELIMITER ;

-- Function 3: Get average property price by location
DELIMITER //
CREATE FUNCTION fn_avg_price_by_city(p_city VARCHAR(100))
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_avg_price DECIMAL(12,2);
    
    SELECT COALESCE(AVG(p.price), 0) INTO v_avg_price
    FROM Properties p
    JOIN Locations l ON p.location_id = l.location_id
    WHERE l.city = p_city AND p.status = 'available';
    
    RETURN v_avg_price;
END//
DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger 1: Update agent rating after new review
DELIMITER //
CREATE TRIGGER tr_update_agent_rating
AFTER INSERT ON Reviews
FOR EACH ROW
BEGIN
    IF NEW.agent_id IS NOT NULL THEN
        UPDATE Agents
        SET rating = (
            SELECT AVG(rating)
            FROM Reviews
            WHERE agent_id = NEW.agent_id
        )
        WHERE agent_id = NEW.agent_id;
    END IF;
END//
DELIMITER ;

-- Trigger 2: Prevent deletion of properties with active appointments
DELIMITER //
CREATE TRIGGER tr_check_property_delete
BEFORE DELETE ON Properties
FOR EACH ROW
BEGIN
    DECLARE active_appointments INT;
    
    SELECT COUNT(*) INTO active_appointments
    FROM Appointments
    WHERE property_id = OLD.property_id 
    AND status = 'scheduled'
    AND appointment_date > NOW();
    
    IF active_appointments > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete property with active appointments';
    END IF;
END//
DELIMITER ;

-- Trigger 3: Auto-cancel appointments when property status changes
DELIMITER //
CREATE TRIGGER tr_cancel_appointments_on_status_change
AFTER UPDATE ON Properties
FOR EACH ROW
BEGIN
    IF NEW.status IN ('sold', 'rented', 'off_market') 
       AND OLD.status = 'available' THEN
        UPDATE Appointments
        SET status = 'cancelled',
            notes = CONCAT(COALESCE(notes, ''), ' - Auto-cancelled due to property status change')
        WHERE property_id = NEW.property_id
        AND status = 'scheduled'
        AND appointment_date > NOW();
    END IF;
END//
DELIMITER ;

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Insert Users
INSERT INTO Users (email, password_hash, first_name, last_name, phone, user_type) VALUES
('admin@realestate.com', 'hashed_password_1', 'John', 'Admin', '555-0100', 'admin'),
('agent1@realestate.com', 'hashed_password_2', 'Sarah', 'Johnson', '555-0101', 'agent'),
('agent2@realestate.com', 'hashed_password_3', 'Michael', 'Smith', '555-0102', 'agent'),
('agent3@realestate.com', 'hashed_password_4', 'Emily', 'Davis', '555-0103', 'agent'),
('client1@email.com', 'hashed_password_5', 'David', 'Wilson', '555-0104', 'client'),
('client2@email.com', 'hashed_password_6', 'Jennifer', 'Brown', '555-0105', 'client'),
('client3@email.com', 'hashed_password_7', 'Robert', 'Taylor', '555-0106', 'client'),
('client4@email.com', 'hashed_password_8', 'Lisa', 'Anderson', '555-0107', 'client'),
('client5@email.com', 'hashed_password_9', 'James', 'Martinez', '555-0108', 'client'),
('agent4@realestate.com', 'hashed_password_10', 'Amanda', 'Garcia', '555-0109', 'agent');

-- Insert PropertyTypes
INSERT INTO PropertyTypes (type_name, description) VALUES
('Single Family Home', 'Detached single-family residential property'),
('Condo', 'Condominium unit in a multi-unit building'),
('Townhouse', 'Multi-floor home sharing walls with adjacent properties'),
('Apartment', 'Rental unit in a multi-unit building'),
('Commercial', 'Commercial real estate property'),
('Land', 'Vacant land for development'),
('Multi-Family', 'Property with multiple residential units');

-- Insert Locations
INSERT INTO Locations (street_address, city, state, zip_code, latitude, longitude) VALUES
('123 Main Street', 'Boston', 'Massachusetts', '02108', 42.3601, -71.0589),
('456 Oak Avenue', 'Cambridge', 'Massachusetts', '02139', 42.3736, -71.1097),
('789 Elm Street', 'Somerville', 'Massachusetts', '02144', 42.3876, -71.0995),
('321 Pine Road', 'Brookline', 'Massachusetts', '02445', 42.3318, -71.1212),
('654 Maple Drive', 'Newton', 'Massachusetts', '02458', 42.3370, -71.2092),
('987 Cedar Lane', 'Quincy', 'Massachusetts', '02169', 42.2529, -71.0023),
('147 Birch Court', 'Waltham', 'Massachusetts', '02451', 42.3765, -71.2356),
('258 Spruce Way', 'Medford', 'Massachusetts', '02155', 42.4184, -71.1062),
('369 Willow Street', 'Arlington', 'Massachusetts', '02474', 42.4154, -71.1565),
('741 Ash Boulevard', 'Watertown', 'Massachusetts', '02472', 42.3709, -71.1828);

-- Insert Agents
INSERT INTO Agents (user_id, license_number, agency_name, commission_rate, specialization, years_experience) VALUES
(2, 'MA-RE-001234', 'Prime Realty Group', 3.00, 'Residential', 8),
(3, 'MA-RE-005678', 'Coastal Properties', 2.75, 'Luxury Homes', 12),
(4, 'MA-RE-009012', 'Metro Real Estate', 3.25, 'Commercial', 5),
(10, 'MA-RE-003456', 'Urban Living Realty', 3.00, 'Condos & Apartments', 6);

-- Insert Clients
INSERT INTO Clients (user_id, preferred_contact_method, budget_min, budget_max, preferred_location, looking_for) VALUES
(5, 'email', 300000, 500000, 'Boston', 'buy'),
(6, 'phone', 400000, 700000, 'Cambridge', 'buy'),
(7, 'text', 2000, 3000, 'Somerville', 'rent'),
(8, 'email', 500000, 800000, 'Brookline', 'buy'),
(9, 'email', 1500, 2500, 'Boston', 'rent');

-- Insert Properties
INSERT INTO Properties (location_id, property_type_id, agent_id, title, description, price, listing_type, bedrooms, bathrooms, square_feet, lot_size, year_built, listed_date, parking_spaces, has_garage) VALUES
(1, 1, 1, 'Beautiful Victorian Home in Downtown Boston', 'Stunning 3-bedroom Victorian with modern updates, hardwood floors, and city views.', 675000, 'sale', 3, 2.5, 2200, 3500, 1895, '2024-10-15', 2, TRUE),
(2, 2, 2, 'Modern Luxury Condo in Cambridge', 'High-end 2-bedroom condo with floor-to-ceiling windows, granite countertops, and rooftop access.', 850000, 'sale', 2, 2.0, 1400, NULL, 2018, '2024-10-20', 1, FALSE),
(3, 3, 1, 'Charming Townhouse in Somerville', 'Spacious 3-bedroom townhouse with private patio and updated kitchen.', 550000, 'sale', 3, 2.5, 1800, 2000, 2005, '2024-10-22', 2, TRUE),
(4, 1, 2, 'Family Home in Brookline', 'Large 4-bedroom home with finished basement, big backyard, and near schools.', 925000, 'sale', 4, 3.0, 2800, 5000, 1960, '2024-10-18', 2, TRUE),
(5, 2, 3, 'Contemporary Condo in Newton', 'Bright 1-bedroom condo with open floor plan and balcony.', 425000, 'sale', 1, 1.0, 850, NULL, 2020, '2024-10-25', 1, FALSE),
(6, 4, 1, 'Downtown Apartment for Rent', 'Modern 2-bedroom apartment in prime location with amenities.', 3200, 'rent', 2, 1.0, 1100, NULL, 2015, '2024-10-28', 1, FALSE),
(7, 1, 4, 'Historic Home in Waltham', 'Renovated 3-bedroom colonial with original details preserved.', 625000, 'sale', 3, 2.0, 2000, 4000, 1920, '2024-10-12', 2, TRUE),
(8, 3, 1, 'Modern Townhouse in Medford', 'Brand new 3-bedroom townhouse with smart home features.', 595000, 'sale', 3, 2.5, 1900, 1500, 2024, '2024-10-30', 2, TRUE),
(9, 4, 4, 'Cozy Studio Apartment', 'Affordable studio in Arlington with utilities included.', 1800, 'rent', 0, 1.0, 500, NULL, 2010, '2024-10-29', 0, FALSE),
(10, 1, 2, 'Waterfront Property in Watertown', 'Exclusive 4-bedroom home with waterfront views and dock access.', 1250000, 'sale', 4, 3.5, 3200, 8000, 2012, '2024-10-14', 3, TRUE);

-- Insert PropertyImages
INSERT INTO PropertyImages (property_id, image_url, caption, is_primary, display_order) VALUES
(1, '/images/prop1_main.jpg', 'Front view of Victorian home', TRUE, 1),
(1, '/images/prop1_kitchen.jpg', 'Modern kitchen', FALSE, 2),
(1, '/images/prop1_living.jpg', 'Spacious living room', FALSE, 3),
(2, '/images/prop2_main.jpg', 'Luxury condo exterior', TRUE, 1),
(2, '/images/prop2_view.jpg', 'City view from balcony', FALSE, 2),
(3, '/images/prop3_main.jpg', 'Townhouse front', TRUE, 1),
(4, '/images/prop4_main.jpg', 'Family home exterior', TRUE, 1),
(5, '/images/prop5_main.jpg', 'Contemporary condo', TRUE, 1),
(6, '/images/prop6_main.jpg', 'Apartment interior', TRUE, 1),
(7, '/images/prop7_main.jpg', 'Historic home facade', TRUE, 1);

-- Insert Appointments
INSERT INTO Appointments (property_id, client_id, agent_id, appointment_date, duration_minutes, status, notes) VALUES
(1, 1, 1, '2024-11-02 10:00:00', 60, 'scheduled', 'First viewing for interested buyer'),
(2, 2, 2, '2024-11-03 14:00:00', 90, 'scheduled', 'Second viewing, bringing spouse'),
(3, 3, 1, '2024-11-01 16:00:00', 45, 'completed', 'Client very interested'),
(4, 4, 2, '2024-11-04 11:00:00', 60, 'scheduled', 'Family wants to see backyard'),
(6, 5, 1, '2024-11-02 13:00:00', 30, 'scheduled', 'Quick apartment viewing');

-- Insert Transactions
INSERT INTO Transactions (property_id, client_id, agent_id, transaction_type, transaction_date, final_price, commission_amount, payment_status) VALUES
(3, 3, 1, 'sale', '2024-10-30', 545000, 17712.50, 'completed');

-- Insert Reviews
INSERT INTO Reviews (client_id, property_id, agent_id, rating, review_text, is_verified) VALUES
(1, 1, 1, 5, 'Great property and excellent service from Sarah!', TRUE),
(2, 2, 2, 5, 'Michael was very professional and helped us find our dream home.', TRUE),
(3, 3, 1, 4, 'Good experience overall, property was as described.', TRUE),
(4, 4, 2, 5, 'Amazing property in a great location!', FALSE);

-- =====================================================
-- VIEWS FOR REPORTING (BONUS)
-- =====================================================

-- View 1: Available Properties with full details
CREATE VIEW vw_available_properties AS
SELECT 
    p.property_id,
    p.title,
    p.price,
    p.listing_type,
    p.bedrooms,
    p.bathrooms,
    p.square_feet,
    pt.type_name AS property_type,
    CONCAT(l.street_address, ', ', l.city, ', ', l.state, ' ', l.zip_code) AS full_address,
    l.city,
    l.state,
    CONCAT(u.first_name, ' ', u.last_name) AS agent_name,
    u.phone AS agent_phone,
    a.agency_name,
    p.listed_date
FROM Properties p
JOIN PropertyTypes pt ON p.property_type_id = pt.property_type_id
JOIN Locations l ON p.location_id = l.location_id
JOIN Agents a ON p.agent_id = a.agent_id
JOIN Users u ON a.user_id = u.user_id
WHERE p.status = 'available';

-- View 2: Agent Performance Summary
CREATE VIEW vw_agent_performance AS
SELECT 
    a.agent_id,
    CONCAT(u.first_name, ' ', u.last_name) AS agent_name,
    a.agency_name,
    a.years_experience,
    a.rating,
    a.total_sales,
    COUNT(DISTINCT p.property_id) AS active_listings,
    COALESCE(SUM(t.commission_amount), 0) AS total_commission_earned,
    COUNT(DISTINCT t.transaction_id) AS completed_transactions
FROM Agents a
JOIN Users u ON a.user_id = u.user_id
LEFT JOIN Properties p ON a.agent_id = p.agent_id AND p.status = 'available'
LEFT JOIN Transactions t ON a.agent_id = t.agent_id AND t.payment_status = 'completed'
GROUP BY a.agent_id, u.first_name, u.last_name, a.agency_name, 
         a.years_experience, a.rating, a.total_sales;


USE real_estate_db;

-- Add missing Django User fields
ALTER TABLE Users 
ADD COLUMN last_login DATETIME NULL AFTER password_hash,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE AFTER is_active,
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE AFTER is_superuser,
ADD COLUMN date_joined DATETIME DEFAULT CURRENT_TIMESTAMP AFTER is_staff;

-- Update your superuser to have admin privileges
UPDATE Users 
SET is_superuser = TRUE, 
    is_staff = TRUE,
    user_type = 'admin'
WHERE email = 'vaibhavsankaran24@gmail.com';

-- Add username column
ALTER TABLE Users 
ADD COLUMN username VARCHAR(150) NULL UNIQUE AFTER email;

-- Set username to be the same as email for existing users
UPDATE Users SET username = email WHERE username IS NULL;

-- checking if user exists cos login isn't working
USE real_estate_db;
SELECT user_id, email, first_name, last_name, user_type, is_superuser, is_staff, is_active
FROM Users 
WHERE email = 'vaibhavsankaran24@gmail.com';

-- creating a superuser proeprly again
USE real_estate_db;

-- Create the superuser manually
INSERT INTO Users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    phone, 
    user_type,
    username,
    is_active,
    is_superuser,
    is_staff,
    created_at,
    updated_at,
    date_joined
) VALUES (
    'vaibhavsankaran24@gmail.com',
    'pbkdf2_sha256$600000$temp$temp',  -- temporary password
    'Vaibhav',
    'Sankaran',
    '555-0000',
    'admin',
    'vaibhavsankaran24@gmail.com',
    TRUE,
    TRUE,
    TRUE,
    NOW(),
    NOW(),
    NOW()
); 

USE real_estate_db;
SELECT user_id, email, username, first_name, last_name, user_type, is_superuser, is_staff, is_active, password_hash,
       LENGTH(password_hash) as password_length
FROM Users 
WHERE email = 'vaibhavsankaran24@gmail.com';

-- Update PropertyImages table with your new image names
UPDATE PropertyImages SET image_url = '/static/images/prop1_exterior.jpg' WHERE property_id = 1 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/prop1_bed1.jpg' WHERE property_id = 1 AND caption = 'Modern kitchen';

UPDATE PropertyImages SET image_url = '/static/images/prop2_exterior.jpg' WHERE property_id = 2 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/prop2_bed1.jpg' WHERE property_id = 2 AND caption = 'City view from balcony';
UPDATE PropertyImages SET image_url = '/static/images/prop2_bed2.jpg' WHERE property_id = 2 AND display_order = 3;

UPDATE PropertyImages SET image_url = '/static/images/prop3_exterior.jpg' WHERE property_id = 3 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/prop3_bed1.jpg' WHERE property_id = 3 AND display_order = 2;

UPDATE PropertyImages SET image_url = '/static/images/apart4_exterior.jpg' WHERE property_id = 4 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/studio_interior.jpg' WHERE property_id = 4 AND display_order = 2;

UPDATE PropertyImages SET image_url = '/static/images/apart5_exterior.jpg' WHERE property_id = 5 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/apart5_bed1.jpg' WHERE property_id = 5 AND display_order = 2;

UPDATE PropertyImages SET image_url = '/static/images/apart6_exterior.jpg' WHERE property_id = 6 AND is_primary = TRUE;
UPDATE PropertyImages SET image_url = '/static/images/apart6_bed.jpg' WHERE property_id = 6 AND display_order = 2;

-- For properties 7-10 that don't have specific images, we can reuse some
UPDATE PropertyImages SET image_url = '/static/images/prop1_exterior.jpg' WHERE property_id = 7;
UPDATE PropertyImages SET image_url = '/static/images/prop2_exterior.jpg' WHERE property_id = 8;
UPDATE PropertyImages SET image_url = '/static/images/prop3_exterior.jpg' WHERE property_id = 9;
UPDATE PropertyImages SET image_url = '/static/images/apart5_exterior.jpg' WHERE property_id = 10;

-- Property 7 (Historic Home in Waltham)
INSERT INTO PropertyImages (property_id, image_url, caption, is_primary, display_order) VALUES
(7, '/static/images/prop1_exterior.jpg', 'Historic Home Exterior', TRUE, 1),
(7, '/static/images/prop1_bed1.jpg', 'Master Bedroom', FALSE, 2);

-- Property 8 (Modern Townhouse in Medford)
INSERT INTO PropertyImages (property_id, image_url, caption, is_primary, display_order) VALUES
(8, '/static/images/prop2_exterior.jpg', 'Modern Townhouse', TRUE, 1),
(8, '/static/images/prop2_bed1.jpg', 'Spacious Bedroom', FALSE, 2);

-- Property 9 (Cozy Studio Apartment)
INSERT INTO PropertyImages (property_id, image_url, caption, is_primary, display_order) VALUES
(9, '/static/images/studio_interior.jpg', 'Studio Interior', TRUE, 1),
(9, '/static/images/prop3_bed1.jpg', 'Living Space', FALSE, 2);

-- Property 10 (Waterfront Property in Watertown)
INSERT INTO PropertyImages (property_id, image_url, caption, is_primary, display_order) VALUES
(10, '/static/images/apart5_exterior.jpg', 'Waterfront Property', TRUE, 1),
(10, '/static/images/apart6_exterior.jpg', 'Property View', FALSE, 2);

SELECT p.property_id, p.title, COUNT(pi.image_id) as image_count
FROM Properties p
LEFT JOIN PropertyImages pi ON p.property_id = pi.property_id
GROUP BY p.property_id, p.title
ORDER BY p.property_id;
-- =====================================================
-- END OF SCHEMA
-- =====================================================