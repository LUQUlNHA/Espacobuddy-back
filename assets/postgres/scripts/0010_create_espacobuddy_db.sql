CREATE DATABASE espacobuddy;

\c espacobuddy

CREATE EXTENSION IF NOT EXISTS dblink;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- Certifique-se de que a extensão pgcrypto está instalada para gerar UUIDs aleatórios.