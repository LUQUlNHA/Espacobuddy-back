\c espacobuddy

CREATE TABLE IF NOT EXISTS feeders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO feeders (name) VALUES
('Alimentador 1');