# 📋 AquaAlert — Guía de Referencia Git, GitHub & DevOps
> Lecciones aprendidas en el proceso de desarrollo
> Proyecto: AquaAlert IoT Platform — Guadalajara, Jalisco 🇲🇽

---

## 🌿 Flujo de trabajo (GitHub Flow)

```
main  ──●────────────●────────────●────────────●──
         \          /  \          /  \          /
          feat/xxx─●    fix/yyy──●    chore/zzz●
          (1-3 días)    (horas)       (1 día)
```

### Reglas de oro
```
1. NUNCA pushear directo a main → solo PRs
2. Una rama = una cosa específica
3. Ramas cortas → máximo 3 días de vida
4. Siempre partir de main actualizado
5. NUNCA usar sudo con comandos git o archivos del proyecto
6. Verificar git status ANTES de cualquier checkout
7. Mergear PR ANTES de borrar la rama
8. La VM de Azure es solo para git pull y docker — nunca crear ramas ahí
9. Si hay error de permisos → chown primero, nunca sudo git
```

---

## 🔄 Flujo completo de una rama (copy-paste)

```bash
# ── 1. Partir siempre de main actualizado ─────────────
git checkout main
git pull origin main

# ── 2. Crear rama ─────────────────────────────────────
git checkout -b tipo/nombre-descriptivo

# ── 3. Hacer cambios + verificar estado ───────────────
git status        # antes de cualquier checkout
git add .
git commit -m "tipo(scope): descripción en imperativo"

# ── 4. Push ───────────────────────────────────────────
git push -u origin tipo/nombre-descriptivo

# ── 5. Crear PR ───────────────────────────────────────
gh pr create \
  --base main \
  --title "tipo(scope): descripción" \
  --body "Detalle de qué hace este PR"

# ── 6. Mergear PR ← NO OLVIDAR ESTE PASO ─────────────
gh pr merge N --squash --delete-branch

# ── 7. Actualizar main local + limpiar ────────────────
git checkout main && git pull && git branch -d tipo/nombre-rama
```

---

## 📝 Convención de commits (Conventional Commits)

```
tipo(scope): descripción corta en imperativo

Tipos:
  feat      → nueva funcionalidad
  fix       → corrección de bug
  chore     → infra, configs, dependencias
  docs      → solo documentación
  test      → agregar o corregir tests
  refactor  → refactor sin cambio de comportamiento
  ci        → cambios en GitHub Actions / pipelines

Ejemplos reales del proyecto:
  feat(api): add FastAPI application entry point with lifespan
  feat(decoder): implement JSN-SR04T payload decoder
  feat(mqtt): add async MQTT client for ChirpStack uplinks
  feat(alerts): add threshold evaluation and Telegram notifications
  feat(grafana): add water level monitoring dashboard
  fix(deps): remove explicit paho-mqtt pin causing conflict
  fix(test): correct battery_pct rounding assertion
  fix(lint): use is_(True) instead of == True in SQLAlchemy query
  fix(chirpstack): correct TOML integration syntax
  fix(api): remove invalid typing import for list
  fix(devices): normalize device_eui to uppercase on registration
  fix(docker): pass TIMESCALE vars and TELEGRAM_CHAT_ID to api service
  fix(grafana): pass TIMESCALE credentials to grafana container
  fix(grafana): fix alert_level panel using CASE numeric conversion
  fix(grafana): regenerate dashboard JSON with clean encoding
  chore(docker): add full stack docker-compose
  chore(chirpstack): add ChirpStack v4 network server config
  ci: implement real CI pipeline with pytest and docker build
  ci(deploy): add SSH deploy workflow to VPS
```

---

## 🏷️ Nomenclatura de ramas

```
feat/fastapi-main          fix/ci-requirements-conflict
feat/mqtt-services         fix/test-battery-pct-rounding
feat/sensor-models         fix/ruff-e712-sensors
feat/rest-endpoints        fix/docker-compose-env-vars
feat/node-simulator        fix/chirpstack-toml-syntax
feat/grafana-dashboard     fix/chirpstack-postgres-setup
chore/infra-base           fix/chirpstack-env-dsn
chore/docker-compose       fix/config-typing-import
chore/chirpstack-cfg       fix/device-eui-normalize
chore/grafana-provisioning fix/grafana-datasource-credentials
ci/github-actions          fix/grafana-dashboard-units
docs/readme-badges         fix/grafana-alert-panel-final
docs/git-workflow-guide    fix/grafana-json-encoding
test/decoder-unit-tests
```

---

## 🔒 Branch Protection — Ruleset en GitHub

### Configuración:
```
Settings → Rules → Rulesets → Edit

Enforcement status:  Active ✅
Target branches:     Include default branch ✅

Protecciones:
  ✅ Require a pull request before merging
       └─ Required approvals: 0  ← solo developer
       └─ Dismiss stale reviews: ✅
  ✅ Require linear history
  ✅ Require status checks: test-api
       └─ Require branches to be up to date: ✅
  ❌ Todo lo demás

Notas:
  - Repos PRIVADOS con Free no aplican reglas → hacer PÚBLICO
  - test-api aparece en dropdown solo después de correr CI una vez
  - Si no aparece en dropdown → escribirlo manualmente está bien
```

### Verificar protección:
```bash
echo "test" >> README.md
git add . && git commit -m "test: direct push blocked"
git push origin main
# Debe salir: "Changes must be made through a pull request" ✅
git reset --hard HEAD~1
```

---

## 🔒 Merge — Situaciones especiales

```bash
# Merge normal (con CI activo):
gh pr merge N --squash --delete-branch

# Admin override (CI placeholder):
gh pr merge N --squash --delete-branch --admin

# Si --admin falla con "Required status check expected":
# → Desmarcar temporalmente "Require status checks" en Ruleset
# → Mergear → volver a activar

# Auto-merge cuando pasen los checks:
gh pr merge N --squash --delete-branch --auto
```

---

## ⚠️ Errores Git comunes y soluciones

### "no se puede pull con rebase: tienes cambios sin marcar"
```bash
# Opción A — commit:
git add . && git commit -m "tipo: descripción"
# Opción B — stash:
git stash push -m "WIP descripción"
git checkout main
git checkout mi-rama && git stash pop
```

### Ramas remotas huérfanas
```bash
git push origin --delete nombre-rama
git fetch --prune
git branch -a
```

### Creé una rama en Azure por error
```bash
git checkout main   # solo regresar, nunca commitear desde Azure
git status          # debe estar limpio
```

### "Permiso denegado" en git pull en Azure VM
```bash
# Causa: archivos con dueño root en el proyecto
sudo chown -R azureuser:azureuser ~/aquaalert-platform/
git checkout -- archivo-con-cambios-locales
git pull origin main
# Regla: nunca sudo con archivos del proyecto
#        si hay error de permisos → chown primero
```

---

## 🔍 Comandos de diagnóstico frecuentes

```bash
git status                    # estado del árbol
git log --oneline -10         # historial limpio
git branch -a                 # todas las ramas
gh pr list                    # PRs abiertos
gh pr checks N                # estado CI en PR
gh run list --limit 5         # últimos runs Actions
gh run view <ID> --log-failed # log del run fallido
git diff                      # diferencias sin commitear
git fetch --prune             # sincronizar y limpiar refs
```

---

## 🐛 Bugs encontrados — CI (GitHub Actions)

### Bug 1 — Conflicto de dependencias paho-mqtt
```
Síntoma: CI falla en "Install dependencies"
Causa:   paho-mqtt==2.0.0 explícito en requirements.txt
         aiomqtt==2.0.0 requiere paho-mqtt>=1.6.0,<2.0.0
Fix:     Eliminar paho-mqtt del requirements.txt
         Dejar que aiomqtt gestione la dependencia transitiva
```

### Bug 2 — Test con valor de redondeo incorrecto
```
Síntoma: assert 67 == 66 → FAILED
Causa:   round((3800-3000)/(4200-3000)*100) = 66.666 → round() = 67
         El test esperaba 66, el decoder calculaba 67 (correcto)
Fix:     Corregir el assert en test_decoder.py: == 67
Lección: El decoder estaba bien — el test estaba mal
```

### Bug 3 — Ruff E712 en SQLAlchemy query
```
Síntoma: ruff E712: Avoid equality comparisons to True
Causa:   Device.is_active == True en sensors.py
Fix:     Device.is_active.is_(True)
         SQLAlchemy tiene método específico para booleans
```

---

## 🐛 Bugs encontrados — Docker Compose (Azure VM)

### Bug 4 — ChirpStack TOML sintaxis incorrecta
```
Síntoma: TOML parse error at line 43: invalid type map, expected sequence
Causa:   [[integration]] con dobles corchetes = array de tablas en TOML
Fix:     Cambiar a [integration] con corchetes simples
         [[tabla]] = múltiples instancias (array)
         [tabla]   = tabla única ← lo que necesitamos
```

### Bug 5 — ChirpStack no interpola variables en TOML
```
Síntoma: password authentication failed for user "${POSTGRES_USER}"
Causa:   ChirpStack lee el TOML literalmente, no interpola ${VAR}
Fix:     Usar env var POSTGRESQL__DSN en docker-compose.yml
         ChirpStack v4 soporta override via env vars con doble guión bajo
         Ejemplo: POSTGRESQL__DSN=postgresql://user:pass@host/db
```

### Bug 6 — Extensión pg_trgm faltante en PostgreSQL
```
Síntoma: operator class "gin_trgm_ops" does not exist for access method "gin"
Causa:   ChirpStack v4 requiere pg_trgm para índices GIN
         El init.sql no incluía esta extensión
Fix A (volumen nuevo):
         CREATE EXTENSION IF NOT EXISTS "pg_trgm"; en init.sql
Fix B (volumen existente):
         docker compose exec postgres psql -U chirpstack \
           -d chirpstack -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
Lección: init.sql solo se ejecuta cuando el volumen NO existe
         Si el volumen ya existe → agregar extensión manualmente
```

### Bug 7 — ImportError en Python 3.12 con typing
```
Síntoma: ImportError: cannot import name 'list' from 'typing'
Causa:   from typing import list ← inválido en Python 3.9+
         list es un built-in genérico desde Python 3.9
Fix:     Eliminar la línea — usar list directamente como tipo
Lección: Python 3.9+: list[str], dict[str, int] sin importar typing
```

### Bug 8 — API no recibía variables de TimescaleDB
```
Síntoma: API no conectaba a TimescaleDB
Causa:   docker-compose.yml pasaba DATABASE_URL hardcodeado
         pero config.py construye la URL desde variables individuales
Fix:     Pasar TIMESCALE_USER, TIMESCALE_PASSWORD, TIMESCALE_DB
         También faltaba TELEGRAM_CHAT_ID en el bloque env del api
```

### Bug 9 — Device EUI case mismatch
```
Síntoma: mqtt.unknown_device aunque el device estaba registrado
Causa:   MQTT client normaliza EUI a mayúsculas (.upper())
         pero POST /api/v1/devices guardaba el EUI como llegaba
         "a840411d3181bd6b" en DB vs "A840411D3181BD6B" en MQTT
Fix:     data.device_eui = data.device_eui.upper() en el endpoint POST
Lección: Normalizar inputs en el punto de entrada siempre
         Un mismo dato debe tener un único formato en todo el sistema
```

### Bug 10 — Credenciales ChirpStack vs .env
```
Síntoma: password authentication failed for user "chirpstack"
Causa:   chirpstack.toml tenía credenciales hardcodeadas
         pero el .env tenía credenciales diferentes
Fix temporal: Igualar .env a las credenciales del toml para arrancar
Fix permanente: POSTGRESQL__DSN env var en docker-compose.yml
Lección: Definir UN solo lugar para las credenciales
```

---

## 🐛 Bugs encontrados — Grafana

### Bug 11 — Permission denied en git pull en Azure VM
```
Síntoma: error: unable to create file grafana/dashboards/water-level.json: Permission denied
Causa:   Carpeta grafana/dashboards/ con dueño root
         (creada con sudo en algún momento anterior)
Fix:     sudo chown -R azureuser:azureuser ~/aquaalert-platform/
         git checkout -- archivos-con-cambios-locales
         git pull origin main
Lección: NUNCA usar sudo con archivos del proyecto en Azure
         Si hay error de permisos → chown primero, luego git
```

### Bug 12 — Grafana sin credenciales TimescaleDB
```
Síntoma: "Template variable service failed error when executing the sql query"
         Todos los panels mostraban "No data"
Causa:   datasources.yml usa ${TIMESCALE_USER} y ${TIMESCALE_PASSWORD}
         pero esas variables no estaban en el bloque env del servicio grafana
Fix:     Agregar al docker-compose.yml en el servicio grafana:
           - TIMESCALE_USER=${TIMESCALE_USER}
           - TIMESCALE_PASSWORD=${TIMESCALE_PASSWORD}
Lección: Grafana resuelve vars de entorno en datasources.yml
         pero solo las que están en su propio entorno de contenedor
```

### Bug 13 — JSON con newlines literales en rawSql
```
Síntoma: Invalid control character at: line 310 column 34
Causa:   Al editar el dashboard en la UI de Grafana y copiar el JSON,
         el rawSql quedó con saltos de línea y tabs literales
         en lugar de secuencias de escape \n y \t
Fix:     Regenerar el archivo completo desde Python:
         json.dump() serializa correctamente todos los chars especiales
         Nunca copiar JSON de la UI de Grafana directamente al archivo
Lección: Para editar dashboards de Grafana en código:
         OPCIÓN A → editar el JSON a mano en el editor (con cuidado)
         OPCIÓN B → generar el JSON con Python (más seguro)
         NUNCA → copiar el texto del editor de la UI al archivo
```

### Bug 14 — Panel alert_level mostraba "No data"
```
Síntoma: Panel "Nivel de Alerta" mostraba "No data" en Grafana
Causa:   Grafana no puede graficar columnas de texto (VARCHAR)
         en formato time_series — solo acepta valores numéricos
Fix:     Usar CASE SQL para convertir texto a número:
           CASE alert_level
             WHEN 'NORMAL'   THEN 0
             WHEN 'WATCH'    THEN 1
             WHEN 'WARNING'  THEN 2
             WHEN 'CRITICAL' THEN 3
             ELSE 0
           END as "Alerta"
         Luego value mappings convierten 0→🟢 NORMAL, etc.
Lección: Grafana time_series solo acepta columnas numéricas
         Para mostrar texto con colores: número + value mappings
```

---

## 🐳 Docker — Lecciones aprendidas

### Arrancar el stack por etapas (no todo a la vez)
```bash
# Etapa 1 — infraestructura base
docker compose up -d postgres timescaledb redis mosquitto
sleep 10 && docker compose ps

# Etapa 2 — ChirpStack
docker compose up -d chirpstack chirpstack-gateway-bridge
sleep 15 && docker compose logs --tail=20 chirpstack

# Etapa 3 — Aplicación
docker compose up -d api grafana
sleep 20 && docker compose logs --tail=15 api

# Etapa 4 — Simulador
docker compose up -d node-simulator
sleep 10 && docker compose logs --tail=20 node-simulator
```

### Recrear un servicio limpiamente
```bash
docker compose stop servicio
docker compose rm -f servicio
docker compose up -d servicio
docker compose logs --tail=20 servicio
```

### Recrear con volumen limpio
```bash
docker compose stop servicio
docker compose rm -f servicio
docker volume rm aquaalert-platform_nombre_data
docker compose up -d servicio
```

### init.sql solo corre cuando el volumen NO existe
```bash
# Si el volumen ya existe, ejecutar SQL manualmente:
docker compose exec postgres psql -U usuario -d db -c "SQL aquí"
```

### Warning "version is obsolete"
```yaml
# Eliminar la primera línea del docker-compose.yml:
version: '3.8'   ← borrar esto
# Docker Compose v2 no requiere esta línea
```

---

## ☁️ Azure VM — Reglas de uso

```
✅ git clone (una sola vez al inicio)
✅ git pull origin main (para actualizar)
✅ docker compose up/down/logs/ps/restart
✅ docker compose exec (para diagnóstico)
❌ git checkout -b (nunca crear ramas aquí)
❌ git commit (nunca commitear desde Azure)
❌ git push (nunca pushear desde Azure)
❌ sudo con archivos del proyecto

Regla fundamental:
  Azure = servidor de ejecución
  Laptop = entorno de desarrollo
```

### Puertos abiertos en Azure NSG
```
8080/TCP → ChirpStack UI     (admin/admin — cambiar en producción)
8000/TCP → FastAPI + Swagger (/docs)
3000/TCP → Grafana           (admin/GRAFANA_PASSWORD)
1883/TCP → MQTT broker
1700/UDP → LoRaWAN Gateway Bridge (para Dragino)
```

---

## 📊 Verificación del pipeline end-to-end

```bash
# Estado de todos los servicios
docker compose ps

# Lecturas en tiempo real (API)
curl -s http://localhost:8000/api/v1/sensors/A840411D3181BD6B/latest \
  | python3 -m json.tool

# Historial última hora
curl -s "http://localhost:8000/api/v1/sensors/A840411D3181BD6B/readings?hours=1" \
  | python3 -m json.tool

# Ver lecturas en TimescaleDB
docker compose exec timescaledb psql -U aquaalert -d aquaalert_ts \
  -c "SELECT time, distance_cm, water_level_cm, fill_pct, alert_level
      FROM sensor_readings ORDER BY time DESC LIMIT 5;"

# Logs del pipeline completo
docker compose logs --tail=10 api
docker compose logs --tail=10 node-simulator
```

---

## 🌐 Ruleset — Status Check

```
Cuándo activar "Require status checks: test-api":
  → Después de que el CI haya corrido verde al menos una vez

Cuándo desactivarlo temporalmente:
  → Si el status check bloquea un merge urgente
  → Desmarcar → mergear → volver a activar

Cuándo ya no necesitas --admin:
  → Cuando test-api esté configurado en el Ruleset
    y el CI valide automáticamente cada PR
```

---

## 📦 Historial de ramas — Progreso completo

### ✅ Fase 1 — Base del proyecto (10 ramas)
```
✅ chore/infra-base           → mosquitto, postgres, nginx, .env, README
✅ chore/docker-compose       → docker-compose.yml completo (9 servicios)
✅ feat/api-core              → requirements, Dockerfile, config, database
✅ feat/sensor-models         → SensorReading y Device ORM (TimescaleDB)
✅ feat/rest-endpoints        → routers sensors y devices (CRUD completo)
✅ feat/node-simulator        → simulador CubeCell + JSN-SR04T via MQTT
✅ chore/grafana-provisioning → datasources y dashboards auto-provisioned
✅ test/decoder-unit-tests    → tests unitarios decoder con pytest
✅ docs/readme-badges         → badges CI, license, LoRaWAN, Jalisco 🇲🇽
✅ docs/git-workflow-guide    → esta guía en docs/FLUJO-TRABAJO-GIT.md
```

### ✅ Fase 2 — Lógica de negocio (4 ramas)
```
✅ feat/fastapi-main     → main.py: lifespan, CORS, routers, /health
✅ feat/mqtt-services    → decoder.py + alert_service.py + mqtt_client.py
✅ chore/chirpstack-cfg  → chirpstack.toml: PostgreSQL, Redis, US915, MQTT
✅ ci/github-actions     → ci.yml real (pytest + ruff + docker build)
                           deploy.yml (SSH deploy a VPS)
```

### ✅ Fase 3 — Stack en producción (Azure VM)
```
✅ feat/grafana-dashboard       → dashboard 8 panels completo
✅ fix/ci-requirements-conflict → paho-mqtt conflicto deps
✅ fix/test-battery-pct         → assert de redondeo corregido
✅ fix/ruff-e712-sensors        → is_(True) en SQLAlchemy
✅ fix/docker-compose-env-vars  → TIMESCALE vars + TELEGRAM_CHAT_ID
✅ fix/chirpstack-toml-syntax   → [[integration]] → [integration]
✅ fix/chirpstack-postgres-setup→ pg_trgm + DSN env vars
✅ fix/config-typing-import     → from typing import list eliminado
✅ fix/device-eui-normalize     → .upper() en registro de devices
✅ fix/grafana-credentials      → TIMESCALE vars en servicio grafana
✅ fix/grafana-dashboard-units  → suffix:cm + alert_level CASE
✅ fix/grafana-json-encoding    → JSON regenerado desde Python
✅ docs/update-workflow-*       → esta guía actualizada
```

### ✅ Feature GPS — CubeCell AB02S Air530
```
✅ feat/gps-payload-decoder   → decoder tipo A(4B) + tipo B(12B) con GPS
✅ feat/gps-db-model          → columnas lat/lon en TimescaleDB + migración
✅ feat/gps-simulator         → GPS cada 10 uplinks con ruido realista ~5m
✅ feat/gps-grafana-map       → Geomap + panels Latitud/Longitud
✅ fix/simulator-requirements → aiomqtt faltaba en requirements.txt
✅ fix/simulator-device-eui   → devEui vs deviceEui en mensaje ChirpStack
✅ fix/grafana-gps-coords     → float con decimals=6 en lugar de ROUND::text
```

### 🔜 Fase 4 — Hardware real
```
🔜 Conectar gateway Dragino DLOS8N → UDP :1700 → ChirpStack
🔜 Registrar CubeCell AB02S en ChirpStack UI
🔜 Programar firmware con payload tipo A(4B) y tipo B(12B) con GPS
🔜 Primer uplink GPS real end-to-end
🔜 Calibrar distancia puente/sensor en campo
🔜 Test alertas Telegram con hardware real
🔜 chore/securize-credentials → passwords seguros en producción
🔜 chore/remove-version-key   → eliminar "version: 3.8" del compose
```

---

## 🐛 Bugs encontrados — Feature GPS

### Bug 15 — pip --break-system-packages no existe en Pop OS con venv
```
Síntoma: no such option: --break-system-packages
Causa:   En Pop OS con Python del sistema la flag es válida solo en
         ciertos contextos; dentro de un venv no aplica ni se necesita
Fix:     Crear venv primero, luego pip install normal:
           cd services/api
           python3 -m venv .venv
           source .venv/bin/activate
           pip install -r requirements.txt
           pytest tests/
           deactivate
Lección: En proyectos con venv nunca usar --break-system-packages
         Agregar .venv/ al .gitignore del proyecto
```

### Bug 16 — docker-compose (v1) vs docker compose (v2)
```
Síntoma: KeyError: 'ContainerConfig' al hacer docker-compose up
Causa:   docker-compose 1.29.2 instalado con apt no es compatible
         con imágenes modernas de Docker
Fix:     Usar siempre docker compose (sin guión) — plugin v2 oficial
         docker compose up -d   ← correcto
         docker-compose up -d   ← incorrecto, nunca usar
Lección: En Azure VM verificar con: docker compose version
         Debe mostrar Docker Compose version v2.x.x
```

### Bug 17 — stdin redirection no funciona con docker compose exec
```
Síntoma: "the input device is not a TTY"
Causa:   docker compose exec no acepta redirección < file por stdin
Fix:     Usar -c con el SQL inline:
           docker compose exec timescaledb psql -U user -d db -c "SQL"
         O copiar el archivo al contenedor primero:
           docker compose cp archivo.sql servicio:/tmp/
           docker compose exec servicio psql -U user -d db -f /tmp/archivo.sql
```

### Bug 18 — aiomqtt faltaba en requirements del simulador
```
Síntoma: ModuleNotFoundError: No module named 'aiomqtt'
Causa:   node_simulator.py fue reescrito usando aiomqtt async
         pero requirements.txt del simulador aún tenía paho-mqtt
Fix:     Reemplazar contenido de services/simulator/requirements.txt:
           aiomqtt==2.0.0
Lección: Al reescribir un servicio siempre actualizar requirements.txt
         antes del merge — el CI no corre tests del simulador
```

### Bug 19 — devEui vs deviceEui en mensaje ChirpStack
```
Síntoma: mqtt.no_device_eui aunque el device estaba registrado
Causa:   mqtt_client.py lee deviceInfo.devEui (formato ChirpStack real)
         pero el simulador enviaba deviceInfo.deviceEui
Fix:     En node_simulator.py build_chirpstack_message:
           "devEui": device_eui.upper()   ← correcto
           "deviceEui": ...               ← incorrecto
Lección: El formato exacto del JSON de ChirpStack v4 usa devEui
         Verificar siempre contra la documentación oficial de ChirpStack
         o capturar un mensaje real del gateway para comparar
```

### Bug 20 — ROUND::text causa No data en Grafana stat panel
```
Síntoma: Panels Latitud y Longitud mostraban "No data"
Causa:   Query usaba ROUND(latitude::numeric, 6)::text
         Grafana time_series no puede graficar columnas de texto
Fix:     Usar el float directamente sin cast:
           SELECT time, latitude as "Latitud" FROM ...
         Configurar decimals=6 en fieldConfig del panel
Lección: Grafana time_series solo acepta columnas numéricas
         Para controlar decimales usar fieldConfig.defaults.decimals
         nunca castear a texto dentro del SQL
```

---

## 📡 Diseño del payload GPS — CubeCell AB02S

```
Payload tipo A — 4 bytes (uplinks normales, sin GPS):
  Bytes 0-1: distance_mm  uint16 big-endian
  Bytes 2-3: battery_mv   uint16 big-endian

Payload tipo B — 12 bytes (cada GPS_INTERVAL uplinks):
  Bytes 0-1:  distance_mm  uint16 big-endian
  Bytes 2-3:  battery_mv   uint16 big-endian
  Bytes 4-7:  latitude     int32  big-endian (grados * 1,000,000)
  Bytes 8-11: longitude    int32  big-endian (grados * 1,000,000)

Ejemplos de encoding:
  lat  20.659703 → int32(20659703)  → 0x013B5337
  lon -103.34959 → int32(-103349590)→ 0xF9C2F06A

Decoder detecta tipo por len(data):
  4  bytes → tipo A → has_gps=False → usar última posición conocida
  12 bytes → tipo B → has_gps=True  → actualizar posición en DB
  otro     → inválido → return {}

Estrategia de batería para sensor semi-fijo:
  GPS_INTERVAL=10 → 90% uplinks son 4 bytes (mínimo consumo)
                  → 10% uplinks son 12 bytes (actualización GPS)
  Configurable via env var GPS_INTERVAL en docker-compose.yml
```

---

## 🏗️ Arquitectura del stack

```
Nodo CubeCell AB02S + JSN-SR04T + GPS Air530
    ↓ LoRaWAN 915MHz (US915 sub-band 0)
    ↓ Payload tipo A (4B) cada uplink normal
    ↓ Payload tipo B (12B) cada 10 uplinks con GPS
Gateway Dragino DLOS8N
    ↓ UDP :1700
ChirpStack Gateway Bridge :1700
    ↓ MQTT → mosquitto:1883
ChirpStack v4 Network Server :8080
    ↓ MQTT topic: application/+/device/+/event/up
FastAPI mqtt_client.py
    ├── decoder.py       → bytes → distance_cm, battery_pct
    │                      + latitude, longitude (payload tipo B)
    ├── alert_service.py → fill_pct → NORMAL/WATCH/WARNING/CRITICAL
    │                      → Telegram Bot notificaciones push
    └── TimescaleDB      → SensorReading hypertable
         columns: distance_cm, water_level_cm, fill_pct,
                  battery_mv, battery_pct, rssi, snr,
                  alert_level, latitude, longitude
         ↓
      Grafana :3000      → 11 panels en tiempo real
         ├── Estado actual (4 stats)
         ├── Histórico (timeseries + gauge)
         ├── Señal LoRa y Batería (2 timeseries)
         └── Ubicación GPS (Geomap + Latitud + Longitud)
      /docs   :8000      → Swagger UI

Simulador (desarrollo sin hardware):
  node_simulator.py → MQTT → mismo pipeline ↑
  GPS_INTERVAL=10   → payload B cada 10 uplinks
  BASE_LAT/LON      → coordenadas configurables por env var
```

---

## 🔑 Acceso a servicios (Azure VM)

```
http://<IP-AZURE>:8000/docs  → FastAPI Swagger UI
http://<IP-AZURE>:8000/health → {"status":"ok","version":"0.1.0"}
http://<IP-AZURE>:8080        → ChirpStack UI (admin/admin)
http://<IP-AZURE>:3000        → Grafana (admin/GRAFANA_PASSWORD)
```

---

## 📱 Alertas Telegram — Niveles

```
🟢 NORMAL   → fill_pct < 50%  → sin notificación
🟡 WATCH    → fill_pct >= 50% → notificación de observación
🟠 WARNING  → fill_pct >= 70% → notificación de advertencia
🔴 CRITICAL → fill_pct >= 85% → notificación crítica

Mensaje incluye:
  - Nombre y ubicación del sensor
  - Nivel de agua en cm
  - Porcentaje de llenado
  - Batería %
  - Device EUI
```

---

*Proyecto: AquaAlert IoT Platform*
*Stack: LoRaWAN + ChirpStack v4 + FastAPI + TimescaleDB + Grafana*
*Hardware: Heltec CubeCell AB02S (GPS Air530) + JSN-SR04T + Dragino DLOS8N*
*CI/CD: GitHub Actions + Docker Compose*
*Infraestructura: Azure VM Ubuntu + Docker*
*Desarrollado en Guadalajara, Jalisco, México 🇲🇽*
