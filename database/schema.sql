CREATE TABLE users(
discord_id BIGINT PRIMARY KEY,
points BIGINT DEFAULT 0
);
CREATE TABLE point_transactions(
id SERIAL PRIMARY KEY,
user_id BIGINT,
amount INT,
source TEXT,
reason TEXT,
created_at TIMESTAMP DEFAULT NOW()
);
