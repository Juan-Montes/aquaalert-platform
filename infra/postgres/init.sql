-- infra/postgres/init.sql
-- Inicialización de bases de datos para ChirpStack

-- Base de datos principal de ChirpStack
CREATE DATABASE chirpstack;

-- Extensión para UUIDs
\c chirpstack
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear usuario de solo lectura para Grafana (opcional)
-- CREATE USER grafana_reader WITH PASSWORD 'grafana_readonly_pass';
-- GRANT CONNECT ON DATABASE chirpstack TO grafana_reader;
