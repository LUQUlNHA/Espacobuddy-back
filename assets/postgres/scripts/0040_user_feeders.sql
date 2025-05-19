-- Habilita a extensão dblink (se ainda não estiver ativa)
CREATE EXTENSION IF NOT EXISTS dblink;

-- Criação da tabela de relacionamento entre usuários e alimentadores
CREATE TABLE IF NOT EXISTS user_feeders (
    user_id UUID NOT NULL, -- UUID do usuário no Keycloak
    feeder_id UUID NOT NULL, -- UUID do alimentador registrado
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Data de associação
    nickname VARCHAR(255) NOT NULL, -- Apelido atribuído pelo usuário
    PRIMARY KEY (user_id, feeder_id),
    CONSTRAINT fk_feeder FOREIGN KEY (feeder_id) REFERENCES feeders(id)
);

-- Função para verificar se o usuário existe no banco Keycloak via dblink
CREATE OR REPLACE FUNCTION check_user_exists(user_uuid UUID) RETURNS BOOLEAN AS $$
DECLARE
    result BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM dblink('dbname=keycloak', 
            'SELECT id FROM users WHERE id = ' || quote_literal(user_uuid)
        ) AS t(id UUID)
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Função que impede inserção se usuário não existir no banco Keycloak
CREATE OR REPLACE FUNCTION validate_user_exists() RETURNS trigger AS $$
BEGIN
    IF NOT check_user_exists(NEW.user_id) THEN
        RAISE EXCEPTION 'Usuário % não existe no banco Keycloak', NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que chama a verificação sempre que um novo registro for inserido
CREATE TRIGGER trg_validate_user_exists
BEFORE INSERT ON user_feeders
FOR EACH ROW
EXECUTE FUNCTION validate_user_exists();
