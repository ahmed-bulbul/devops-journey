-- init.sql — runs once when MySQL container starts for the first time
-- Creates the three service databases

CREATE DATABASE IF NOT EXISTS users_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS orders_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS products_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant appuser access to all service databases
GRANT ALL PRIVILEGES ON users_db.* TO 'appuser'@'%';
GRANT ALL PRIVILEGES ON orders_db.* TO 'appuser'@'%';
GRANT ALL PRIVILEGES ON products_db.* TO 'appuser'@'%';

FLUSH PRIVILEGES;
