Create database LifeCard;

use LifeCard;

CREATE USER 'app'@'localhost' IDENTIFIED BY 'covrigi';
GRANT ALL PRIVILEGES ON lifecard .* TO 'app'@'localhost';
ALTER USER 'app'@'localhost' IDENTIFIED WITH mysql_native_password BY 'covrigi';

CREATE TABLE User (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone VARCHAR(15)
);

CREATE TABLE Card (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    card_code VARCHAR(50) UNIQUE NOT NULL,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES User (id)
);

CREATE TABLE Gym (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    CHECK (length(city) > 2)
);

CREATE TABLE Subscription (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    gym_id INT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20),
    CHECK (status IN ('active', 'expired', 'cancelled')),
    CHECK (end_date > start_date),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (gym_id) REFERENCES Gym(id)
);

CREATE TABLE VisitLog (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    gym_id INT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (gym_id) REFERENCES Gym(id)
);


INSERT INTO Gym (name, address, city) VALUES
('Fitness Plus', '123 Main St', 'Bucuresti'),
('Health Club', '456 Oak St', 'Bucuresti'),
('Power Gym', '789 Pine St', 'Bucuresti'),
('Fit Factory', '101 Maple St', 'Bucuresti'),
('Gold’s Gym', '202 Birch St', 'Bucuresti'),
('Urban Fitness', '303 Cedar St', 'Iasi'),
('Flex Gym', '404 Elm St', 'Iasi'),
('Peak Performance', '505 Willow St', 'Iasi'),
('BodyWorks Gym', '606 Rose St', 'Iasi'),
('Vibe Fitness', '707 Chestnut St', 'Iasi'),
('Iron Works', '808 Vine St', 'Vaslui'),
('Elite Gym', '909 Birchwood St', 'Vaslui'),
('MaxFit', '1001 Oakwood St', 'Vaslui'),
('Core Fitness', '1112 Pinewood St', 'Vaslui'),
('The Gym', '1213 Cedarwood St', 'Vaslui'),
('Fitness Lab', '1314 Elmwood St', 'Vaslui'),
('AllFit Gym', '1415 Rosewood St', 'Vaslui'),
('CrossFit Central', '1516 Chestnutwood St', 'Tecuci'),
('Next Level Fitness', '1617 Willowwood St', 'Tecuci'),
('ActiveFit', '1718 Maplewood St', 'Tecuci'),
('Momentum Gym', '1819 Birchwood St', 'Tecuci'),
('Ironclad Gym', '1920 Pinewood St', 'Tecuci'),
('Train Hard', '2021 Cedarwood St', 'Tecuci'),
('Burn Gym', '2122 Oakwood St', 'Tecuci'),
('Pro Fitness', '2223 Elmwood St', 'Tecuci');

INSERT INTO Subscription (user_id, gym_id, start_date, end_date, status) VALUES
(1, 1, '2025-01-01', '2025-12-31', 'active'),
(2, 2, '2025-02-01', '2025-11-30', 'active'),
(3, 3, '2025-03-01', '2025-09-30', 'expired'),
(4, 4, '2025-04-01', '2025-10-31', 'cancelled'),
(5, 5, '2025-05-01', '2025-12-31', 'active'),
(6, 6, '2025-06-01', '2025-11-30', 'active'),
(7, 7, '2025-07-01', '2025-12-31', 'active'),
(8, 8, '2025-08-01', '2025-10-31', 'expired'),
(9, 9, '2025-09-01', '2025-12-31', 'active'),
(10, 10, '2025-10-01', '2025-11-30', 'cancelled'),
(11, 11, '2025-11-01', '2025-12-31', 'active'),
(12, 12, '2025-12-01', '2025-12-31', 'active'),
(13, 13, '2025-01-01', '2025-12-31', 'expired'),
(14, 14, '2025-02-01', '2025-11-30', 'active'),
(15, 15, '2025-03-01', '2025-09-30', 'cancelled'),
(16, 16, '2025-04-01', '2025-10-31', 'active'),
(17, 17, '2025-05-01', '2025-12-31', 'active'),
(18, 18, '2025-06-01', '2025-11-30', 'cancelled'),
(19, 19, '2025-07-01', '2025-12-31', 'expired'),
(20, 20, '2025-08-01', '2025-10-31', 'active'),
(21, 21, '2025-09-01', '2025-12-31', 'active'),
(22, 22, '2025-10-01', '2025-11-30', 'cancelled'),
(23, 23, '2025-11-01', '2025-12-31', 'active'),
(24, 24, '2025-12-01', '2025-12-31', 'expired'),
(25, 25, '2025-01-01', '2025-12-31', 'active');

INSERT INTO VisitLog (user_id, gym_id) VALUES
(1, 30),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10),
(11, 11),
(12, 12),
(13, 13),
(14, 14),
(15, 15),
(16, 16),
(17, 17),
(18, 18),
(19, 19),
(20, 20),
(21, 21),
(22, 22),
(23, 23),
(24, 24),
(25, 25);

