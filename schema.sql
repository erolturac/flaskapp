-- Run this once against your MySQL server to set up the database.
-- Example:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS flask_auth_demo
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE flask_auth_demo;

CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
