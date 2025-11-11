-- Create database
CREATE DATABASE IF NOT EXISTS stats;
USE stats;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    description TEXT,
    image VARCHAR(255),
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample products
INSERT INTO products (name, category, quantity, price, description, image) VALUES
('HP Laptop', 'Laptop', 15, 45000.00, 'High-performance laptop for business use', 'hp-laptop.jpg'),
('Samsung Galaxy S23', 'Mobile', 25, 75000.00, 'Latest flagship smartphone', 'samsung-s23.jpg'),
('Apple Watch Series 9', 'Smart Watch', 10, 42000.00, 'Advanced smartwatch with health monitoring', 'apple-watch.jpg'),
('Dell XPS 13', 'Laptop', 8, 85000.00, 'Premium ultrabook for professionals', 'dell-xps.jpg'),
('iPhone 15 Pro', 'Mobile', 12, 135000.00, 'Latest iPhone with titanium design', 'iphone-15.jpg');

-- Insert sample locations
INSERT INTO locations (branch_name, city) VALUES
('Main Warehouse', 'Mumbai'),
('South Branch', 'Delhi'),
('East Depot', 'Bengaluru'),
('North Branch', 'Coimbatore'),
('Russov Main Area', 'Kerala');