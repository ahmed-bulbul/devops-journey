-- init.sql — Runs once on first MySQL container start
CREATE DATABASE IF NOT EXISTS users_db    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS orders_db   CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS products_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON users_db.*    TO 'appuser'@'%';
GRANT ALL PRIVILEGES ON orders_db.*   TO 'appuser'@'%';
GRANT ALL PRIVILEGES ON products_db.* TO 'appuser'@'%';

FLUSH PRIVILEGES;
