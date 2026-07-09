CREATE TABLE users(discord_id BIGINT PRIMARY KEY,points BIGINT DEFAULT 0);
CREATE TABLE point_transactions(id SERIAL PRIMARY KEY,user_id BIGINT,amount INT,source TEXT,reason TEXT);
CREATE TABLE daily_checkins(id SERIAL PRIMARY KEY,user_id BIGINT,reward INT,created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE invites(id SERIAL PRIMARY KEY,inviter_id BIGINT,invitee_id BIGINT,status TEXT);
CREATE TABLE message_rewards(id SERIAL PRIMARY KEY,user_id BIGINT,amount INT,created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE products(id SERIAL PRIMARY KEY,name TEXT,price INT,type TEXT,status BOOLEAN DEFAULT TRUE);
CREATE TABLE orders(id SERIAL PRIMARY KEY,user_id BIGINT,product_id INT,status TEXT);
