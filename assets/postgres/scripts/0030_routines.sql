\c espacobuddy

CREATE TABLE IF NOT EXISTS routines (
    id SERIAL PRIMARY KEY,
    routine_name VARCHAR(255) NOT NULL,
    feeder_id UUID NOT NULL REFERENCES feeders(id),
    schedule_time TIME NOT NULL,
    portion_size VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL, -- UUID do usuário no Keycloak
    CONSTRAINT fk_feeder FOREIGN KEY (feeder_id) REFERENCES feeders(id)
); 

-- Trigger que chama a verificação sempre que um novo registro for inserido
CREATE OR REPLACE TRIGGER trg_validate_user_exists_two
BEFORE INSERT ON routines
FOR EACH ROW
EXECUTE FUNCTION validate_user_exists();