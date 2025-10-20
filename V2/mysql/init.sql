CREATE DATABASE IF NOT EXISTS studysense;

USE studysense;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255),
  email VARCHAR(255),
  password_hash VARCHAR(255)
);

CREATE TABLE sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  start_time DATETIME,
  end_time DATETIME,
  focus_score FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  alert_type VARCHAR(255),
  alert_time DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
