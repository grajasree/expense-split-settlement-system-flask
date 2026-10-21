-- Expense Split and Settlement System Database Schema
-- Academic Year 2026

CREATE DATABASE IF NOT EXISTS `expense_settlement_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `expense_settlement_db`;

-- Drop tables in reverse order of foreign keys for clean recreation if needed
DROP TABLE IF EXISTS `expense_splits`;
DROP TABLE IF EXISTS `expenses`;
DROP TABLE IF EXISTS `group_budgets`;
DROP TABLE IF EXISTS `group_members`;
DROP TABLE IF EXISTS `groups`;
DROP TABLE IF EXISTS `users`;

-- 1. Users Table
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Groups Table
CREATE TABLE `groups` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT NULL,
    `created_by` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_group_creator` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Group Members Table
CREATE TABLE `group_members` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `group_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `role` VARCHAR(20) DEFAULT 'member', -- 'creator' or 'member'
    `joined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_group_member` (`group_id`, `user_id`),
    INDEX `idx_member_lookup` (`group_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Group Budgets Table
CREATE TABLE `group_budgets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `group_id` INT NOT NULL UNIQUE,
    `monthly_budget` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Expenses Table
CREATE TABLE `expenses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `group_id` INT NOT NULL,
    `paid_by` INT NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL,
    `category` VARCHAR(50) NOT NULL DEFAULT 'Other',
    `date` DATE NOT NULL,
    `split_type` VARCHAR(20) NOT NULL DEFAULT 'EQUAL', -- 'EQUAL', 'PERCENTAGE', 'CUSTOM'
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`paid_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_expense_group` (`group_id`),
    INDEX `idx_expense_payer` (`paid_by`),
    INDEX `idx_expense_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Expense Splits Table (Participants & individual shares)
CREATE TABLE `expense_splits` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `expense_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `share_amount` DECIMAL(10, 2) NOT NULL,
    `share_percentage` DECIMAL(5, 2) NULL,
    FOREIGN KEY (`expense_id`) REFERENCES `expenses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_expense_participant` (`expense_id`, `user_id`),
    INDEX `idx_split_user` (`user_id`),
    INDEX `idx_split_expense` (`expense_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
