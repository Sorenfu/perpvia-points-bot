CREATE TABLE daily_checkins(
id SERIAL PRIMARY KEY,
user_id BIGINT,
reward INT,
created_at TIMESTAMP DEFAULT NOW()
);
