CREATE DATABASE lost_and_found_india;
USE lost_and_found_india;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    phone_no  VARCHAR(20) NOT NULL,              -- Added phone number field
);

CREATE TABLE Locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);
CREATE TABLE lostitems (
    lost_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    location_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    date_lost DATE NOT NULL,
    phone_no VARCHAR(15) NOT NULL,              -- Added phone number field
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
);

CREATE TABLE founditems (
    found_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    location_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    date_found DATE NOT NULL,
    phone_no VARCHAR(15) NOT NULL,              -- Added phone number field
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
);


CREATE TABLE Matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    lost_id INT NOT NULL,
    found_id INT NOT NULL,
    similarity_score DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_id) REFERENCES LostItems(lost_id),
    FOREIGN KEY (found_id) REFERENCES FoundItems(found_id)
);

-- Sample data for India
INSERT INTO Categories (category_name) VALUES ('Electronics'), ('Jewelry'), ('Clothing'), ('Documents');
INSERT INTO Locations (state, city, country, latitude, longitude) VALUES 
('Delhi', 'New Delhi', 'India', 28.6139, 77.2090),
('Maharashtra', 'Mumbai', 'India', 19.0760, 72.8777),
('Karnataka', 'Bangalore', 'India', 12.9716, 77.5946),
('Tamil Nadu', 'Chennai', 'India', 13.0827, 80.2707),
('West Bengal', 'Kolkata', 'India', 22.5726, 88.3639);