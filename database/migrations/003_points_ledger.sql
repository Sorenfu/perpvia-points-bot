CREATE TABLE IF NOT EXISTS points_ledger(
 id BIGSERIAL PRIMARY KEY,
 user_id BIGINT NOT NULL,
 change_amount INT NOT NULL,
 reason_code VARCHAR(64) NOT NULL,
 detail TEXT,
 created_at TIMESTAMPTZ DEFAULT now()
);
