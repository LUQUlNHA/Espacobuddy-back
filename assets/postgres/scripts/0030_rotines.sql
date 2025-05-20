\c espacobuddy

CREATE TABLE IF NOT EXISTS rotines (
    id SERIAL PRIMARY KEY,
    routine_name VARCHAR(255) NOT NULL,
    feeder_id UUID NOT NULL UNIQUE REFERENCES feeders(id),
    schedule_time TIME NOT NULL,
    portion_size VARCHAR(255) NOT NULL,
); 