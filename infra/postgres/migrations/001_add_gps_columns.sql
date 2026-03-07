-- Migración 001: agregar columnas GPS a sensor_readings
ALTER TABLE sensor_readings
  ADD COLUMN IF NOT EXISTS latitude  FLOAT,
  ADD COLUMN IF NOT EXISTS longitude FLOAT;

-- Verificar
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sensor_readings'
  AND column_name IN ('latitude', 'longitude');
