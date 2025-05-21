\c espacobuddy

CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    feeder_id UUID NOT NULL REFERENCES feeders(id),
    is_routine BOOLEAN,
    created_at TIME NOT NULL
); 

