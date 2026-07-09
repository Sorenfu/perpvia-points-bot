CREATE TABLE message_rewards(
id SERIAL PRIMARY KEY,
user_id BIGINT,
amount INT,
reward_date DATE DEFAULT CURRENT_DATE,
created_at TIMESTAMP DEFAULT NOW()
);
