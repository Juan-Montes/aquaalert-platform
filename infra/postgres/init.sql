-- infra/postgres/init.sql
-- Inicialización de bases de datos para ChirpStack

-- Base de datos principal de ChirpStack
CREATE DATABASE chirpstack;

\c chirpstack

-- Extensiones requeridas por ChirpStack v4
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
-- Crear usuario de solo lectura para Grafana (opcional)
-- CREATE USER grafana_reader WITH PASSWORD 'grafana_readonly_pass';
-- GRANT CONNECT ON DATABASE chirpstack TO grafana_reader;
