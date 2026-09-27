-- =============================================
--  NagarCare Database Schema  v3.0
--  Run: mysql -u root -p < schema.sql
-- =============================================

CREATE DATABASE IF NOT EXISTS nagarcare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nagarcare;

DROP TABLE IF EXISTS complaint_timeline;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    phone      VARCHAR(15)  DEFAULT '',
    password   VARCHAR(255) NOT NULL,
    points     INT          DEFAULT 0,
    badge      VARCHAR(20)  DEFAULT 'newcomer',
    role       ENUM('citizen','admin','officer') DEFAULT 'citizen',
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE complaints (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id       VARCHAR(30) UNIQUE NOT NULL,
    user_id         INT,
    issue_type      VARCHAR(50)  NOT NULL DEFAULT 'general',
    description     TEXT,
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7),
    address         TEXT,
    image_path      VARCHAR(255),
    priority        ENUM('low','medium','high','critical') DEFAULT 'medium',
    department      VARCHAR(100),
    status          ENUM('submitted','assigned','in_progress','resolved','rejected') DEFAULT 'submitted',
    duplicate_count INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status   (status),
    INDEX idx_priority (priority),
    INDEX idx_location (latitude, longitude),
    INDEX idx_type     (issue_type)
);

CREATE TABLE complaint_timeline (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    status       VARCHAR(50) NOT NULL,
    note         TEXT,
    officer_name VARCHAR(100) DEFAULT 'System',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);

-- ── Seed Users (passwords below) ──
-- admin@nagarcare.in  → admin123
-- rahul@test.com      → test123
-- officer@nagarcare.in→ officer123

INSERT INTO users (name,email,phone,password,points,badge,role) VALUES
('Admin User',    'admin@nagarcare.in',   '9999999999',
 'scrypt:32768:8:1$iqhf95e9qvTB3HXQ$bd2c52d2afcb828e41c0b110da123fcd2789f18e42754b43e06cfd2711b8d07ac6ed02e89c8cc74c69f379288c0483c6aa117f330af59c2e05eb350937d3296d',
 0,'platinum','admin'),
('Rahul Sharma',  'rahul@test.com',       '9876543210',
 'scrypt:32768:8:1$9rE2e6awESr50EyL$25f8edcf9d6ff1fcce50ee185a0a81a72b7144150b298ee291c96796490c6c05f49b8a2ed2596dd38e88b0a413dd6dd0f8c23be48b8138cfd26b530736999c69',
 50,'platinum','citizen'),
('Priya Patel',   'priya@test.com',       '9876543211',
 'scrypt:32768:8:1$9rE2e6awESr50EyL$25f8edcf9d6ff1fcce50ee185a0a81a72b7144150b298ee291c96796490c6c05f49b8a2ed2596dd38e88b0a413dd6dd0f8c23be48b8138cfd26b530736999c69',
 30,'gold','citizen'),
('Officer Patil', 'officer@nagarcare.in', '9876543212',
 'scrypt:32768:8:1$BsiVvHF1HdSVFETO$5fe0f560662f33e74d0bb6b32cc0306fdeb12e374af5749f604d18a269e58b329c23d887cd13b2a08cf4fa5893fd7977396c98e9d65ba8ad3e7c298406190eac',
 0,'newcomer','officer');

-- ── Seed Complaints ──
INSERT INTO complaints (ticket_id,user_id,issue_type,description,latitude,longitude,address,priority,department,status) VALUES
('NC20240101001',2,'pothole',      'Large pothole on MG Road causing accidents',   19.8762,75.3433,'MG Road, Aurangabad',       'high',  'Public Works Department',  'resolved'),
('NC20240101002',3,'garbage',      'Garbage dump near residential colony',          19.8790,75.3450,'Ulka Nagari, Aurangabad',   'medium','Municipal Corporation',    'in_progress'),
('NC20240101003',2,'streetlight',  'Street light not working for 3 days',           19.8740,75.3410,'CIDCO Colony, Aurangabad',  'medium','Electricity Board',        'assigned'),
('NC20240101004',3,'water_leakage','Water pipe burst near market flooding road',    19.8800,75.3460,'City Chowk, Aurangabad',    'high',  'Water Supply Department',  'submitted'),
('NC20240101005',2,'sewage',       'Sewage overflow blocking road and footpath',    19.8780,75.3440,'Osmanpura, Aurangabad',     'high',  'Sewage & Sanitation Board','in_progress'),
('NC20240101006',3,'pothole',      'Pothole near school gate very dangerous',       19.8755,75.3425,'Samarth Nagar, Aurangabad', 'high',  'Public Works Department',  'resolved'),
('NC20240101007',2,'graffiti',     'Graffiti on public wall near bus stand',        19.8770,75.3415,'Bus Stand, Aurangabad',     'low',   'Urban Aesthetics Cell',    'submitted');

INSERT INTO complaint_timeline (complaint_id,status,note,officer_name) VALUES
(1,'submitted',   'Complaint received and logged by NagarCare AI','System'),
(1,'assigned',    'Assigned to Public Works Department Ward 3','Officer Patil'),
(1,'in_progress', 'Repair crew dispatched, work started','Officer Patil'),
(1,'resolved',    'Pothole repaired, road surface restored','Officer Patil'),
(2,'submitted',   'Complaint received','System'),
(2,'assigned',    'Assigned to sanitation team','Officer Kumar'),
(2,'in_progress', 'Cleaning crew working on site','Officer Kumar'),
(3,'submitted',   'Complaint received','System'),
(3,'assigned',    'Assigned to MSEB Team B','Officer Deshpande'),
(4,'submitted',   'HIGH PRIORITY — Water emergency logged','System'),
(5,'submitted',   'Complaint received','System'),
(5,'assigned',    'Emergency sewage team dispatched','Officer Rane'),
(5,'in_progress', 'Pump deployed to clear blockage','Officer Rane'),
(6,'submitted',   'Complaint received','System'),
(6,'resolved',    'Pothole near school fixed on priority','Officer Patil'),
(7,'submitted',   'Complaint received','System');
