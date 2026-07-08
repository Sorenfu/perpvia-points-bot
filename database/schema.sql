CREATE TABLE users(user_id BIGINT PRIMARY KEY,points BIGINT DEFAULT 0);
CREATE TABLE role_rewards(role_id BIGINT PRIMARY KEY,points INT);
CREATE TABLE role_reward_history(user_id BIGINT,role_id BIGINT);
CREATE TABLE products(id SERIAL PRIMARY KEY,name TEXT,price INT,stock INT);
CREATE TABLE orders(id SERIAL PRIMARY KEY,user_id BIGINT,product_id INT);
