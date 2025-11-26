-- database.sql
-- This SQL script creates the database and tables required for the Crop Recommendation system.

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS crop_recommendation;

-- Use the created database
USE crop_recommendation;

--
-- Table structure for table `users`
--
-- This table stores user information, including their login credentials and role.
--
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Table structure for table `predictions`
--
-- This table will store the crop predictions made for each user.
-- It has a foreign key relationship with the `users` table.
--
CREATE TABLE `predictions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `nitrogen` int(11) NOT NULL,
  `phosphorus` int(11) NOT NULL,
  `potassium` int(11) NOT NULL,
  `temperature` decimal(5,2) NOT NULL,
  `humidity` decimal(5,2) NOT NULL,
  `ph` decimal(4,2) NOT NULL,
  `rainfall` decimal(7,2) NOT NULL,
  `predicted_crop` varchar(100) NOT NULL,
  `prediction_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `predictions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add new columns to the `predictions` table for the new features
-- You might want to remove the 'temperature' column if 'climate' fully replaces it
-- or keep it if 'climate' is an additional descriptor.
-- For this update, 'climate' is added as a new column, and 'temperature' is kept
-- as the `model.py` and `index.php` still refer to it for the initial numerical input.
-- You can later decide to remove 'temperature' if your model fully shifts to 'climate'.

-- Adding 'climate' column
ALTER TABLE `predictions`
ADD COLUMN `climate` VARCHAR(50) AFTER `potassium`;

-- Adding 'soil_type' column
ALTER TABLE `predictions`
ADD COLUMN `soil_type` VARCHAR(50) AFTER `rainfall`;

-- Adding 'topography' column
ALTER TABLE `predictions`
ADD COLUMN `topography` VARCHAR(50) AFTER `soil_type`;

-- Adding 'water_availability' column
ALTER TABLE `predictions`
ADD COLUMN `water_availability` VARCHAR(50) AFTER `topography`;

-- You can manually set a user to be an admin by running this SQL command:
-- UPDATE users SET role = 'admin' WHERE username = 'your_admin_username';
