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
  feat(models): add SensorReading and Device ORM models
  feat(api): add sensors and devices REST endpoints
  feat(simulator): add LoRa node simulator for dev testing
  fix(mqtt): reconnect on broker timeout
  fix(deps): remove explicit paho-mqtt pin causing conflict
  fix(test): correct battery_pct rounding assertion
  fix(lint): use is_(True) instead of == True in SQLAlchemy query
  fix(chirpstack): correct TOML integration syntax
  fix(chirpstack): add pg_trgm extension and use env vars in DSN
  fix(api): remove invalid typing import for list
  fix(devices): normalize device_eui to uppercase on registration
  fix(docker): pass TIMESCALE vars and TELEGRAM_CHAT_ID to api service
  chore(docker): add full stack docker-compose
  chore(chirpstack): add ChirpStack v4 network server config
  chore(grafana): add datasource and dashboard provisioning
  docs(readme): add status badges
  docs: add git workflow reference guide
  test(decoder): add unit tests for JSN-SR04T payload decoder
  ci: implement real CI pipeline with pytest and docker build
  ci(deploy): add SSH deploy workflow to VPS
```

---

## 🏷️ Nomenclatura de ramas

```
feat/fastapi-main
feat/mqtt-services
feat/sensor-models
feat/rest-endpoints
feat/node-simulator
fix/mqtt-reconnect-timeout
fix/chirpstack-toml-syntax
fix/chirpstack-postgres-setup
fix/chirpstack-env-dsn
fix/config-typing-import
fix/device-eui-normalize
fix/ci-requirements-conflict
fix/test-battery-pct-rounding
fix/ruff-e712-sensors
fix/docker-compose-env-vars
chore/infra-base
chore/docker-compose
chore/chirpstack-cfg
chore/grafana-provisioning
ci/github-actions
docs/readme-badges
docs/git-workflow-guide
test/decoder-unit-tests
```

---

## 🔒 Branch Protection — Ruleset en GitHub

### Configuración del Ruleset:
```
Settings → Rules → Rulesets → Edit

Enforcement status:  Active ✅        ← Disabled = no funciona
Target branches:     Include default branch ✅

Branch protections:
  ✅ Require a pull request before merging
       └─ Required approvals: 0       ← 0 porque eres solo tú
       └─ Dismiss stale reviews when new commits pushed: ✅
  ✅ Require linear history
  ✅ Require status checks to pass    ← activar con CI real
       └─ Require branches to be up to date: ✅
       └─ Add checks → escribir: test-api
  ❌ Todo lo demás

Notas importantes:
  - Repos privados con cuenta Free no aplican las reglas
    → hacer el repo PÚBLICO para que funcionen
  - test-api solo aparece en dropdown después de que
    el CI haya corrido al menos UNA vez exitosamente
  - Si no aparece en dropdown, escribirlo manualmente
```

### Verificar que la protección funciona:
```bash
echo "test" >> README.md
git add . && git commit -m "test: direct push blocked"
git push origin main
# Debe salir: "Changes must be made through a pull request" ✅
git reset --hard HEAD~1
```

---

## 🔒 Merge — Situaciones especiales

### Cuando el merge falla por reglas del ruleset:
```bash
# Error: "Pull request is not mergeable: base branch policy prohibits merge"

# Opción A — Esperar que CI pase:
gh pr checks N
gh pr merge N --squash --delete-branch

# Opción B — Admin override (CI placeholder):
gh pr merge N --squash --delete-branch --admin

# Opción C — Auto-merge cuando pasen checks:
gh pr merge N --squash --delete-branch --auto

# Si --admin falla con "Required status check expected":
# → Desmarcar temporalmente "Require status checks" en Ruleset
# → Mergear → volver a activar el check
```

### Cuándo usar --admin:
```
✅ CI todavía es placeholder
✅ Eres el único desarrollador
❌ NO usar cuando CI real + status check estén activos
```

---

## ⚠️ Errores Git comunes y soluciones

### "no se puede pull con rebase: tienes cambios sin marcar"
```bash
# Solución A — commit:
git add . && git commit -m "tipo: descripción"
# Solución B — stash:
git stash push -m "WIP descripción"
git checkout main
git checkout mi-rama && git stash pop
```

### "rama adelantada a origin/main por 1 commit"
```bash
git push origin main
```

### "rama detrás de origin/main por 1 commit"
```bash
git pull origin main
```

### Warning: "borrando rama que aún no ha sido fusionada"
```bash
# El PR NO fue mergeado → mergear primero
gh pr merge N --squash --delete-branch
git branch -d nombre-rama
```

### "Permiso denegado" al editar archivos
```bash
# Causa: creados con sudo
sudo chown -R $USER:$USER ~/Github/aquaalert-platform/
# NUNCA usar sudo con git o archivos del proyecto
```

### "GH006/GH013 Protected branch update failed"
```bash
# La protección funciona correctamente ✅
git reset --hard HEAD~1
git checkout -b feat/mi-fix
```

### Ramas remotas huérfanas (no se borraron con el PR)
```bash
git push origin --delete nombre-rama
git fetch --prune
git branch -a  # verificar que están limpias
```

### Creé una rama en la VM de Azure por error
```bash
# En Azure: solo regresar a main
git checkout main
git status  # debe estar limpio
# Nunca hacer commits desde Azure — solo desde laptop
```

---

## 🔍 Comandos de diagnóstico frecuentes

```bash
git status                              # estado del árbol
git log --oneline -10                  # historial limpio
git branch -a                          # todas las ramas
gh pr list                             # PRs abiertos
gh pr checks N                         # estado del CI en PR
gh run list --limit 5                  # últimos runs de Actions
gh run view <ID> --log-failed          # log del run fallido
git diff                               # diferencias sin commitear
git fetch --prune                      # sincronizar y limpiar refs
git branch --merged main | grep -v "main" | xargs git branch -d
```

---

## 🐛 Bugs encontrados durante setup del CI (GitHub Actions)

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
Lección: El decoder estaba bien, el test estaba mal
```

### Bug 3 — Ruff E712 en SQLAlchemy query
```
Síntoma: ruff E712 Avoid equality comparisons to True
Causa:   Device.is_active == True en sensors.py
Fix:     Device.is_active.is_(True)
         SQLAlchemy tiene método específico para booleans
```

---

## 🐛 Bugs encontrados durante docker compose up (Azure VM)

### Bug 4 — ChirpStack TOML sintaxis incorrecta
```
Síntoma: TOML parse error at line 43: invalid type map, expected sequence
Causa:   [[integration]] con dobles corchetes define array de tablas
Fix:     Cambiar a [integration] con corchetes simples
         [[tabla]] = array de tablas (múltiples instancias)
         [tabla]   = tabla única (lo que necesitamos)
```

### Bug 5 — ChirpStack no interpola variables en TOML
```
Síntoma: password authentication failed for user "${POSTGRES_USER}"
Causa:   ChirpStack lee el TOML literalmente, no interpola ${VAR}
Fix:     Usar env var POSTGRESQL__DSN en docker-compose.yml
         ChirpStack v4 soporta override de config via env vars
         con notación de doble guión bajo: SECCION__CLAVE=valor
```

### Bug 6 — Extensión pg_trgm faltante en PostgreSQL
```
Síntoma: operator class "gin_trgm_ops" does not exist for access method "gin"
Causa:   ChirpStack v4 requiere pg_trgm para sus índices GIN
         El init.sql no incluía esta extensión
Fix A:   Agregar al init.sql:
         CREATE EXTENSION IF NOT EXISTS "pg_trgm";
Fix B:   Si el volumen ya existe, agregar manualmente:
         docker compose exec postgres psql -U chirpstack \
           -d chirpstack -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
Nota:    init.sql solo se ejecuta cuando el volumen NO existe
         Si el volumen ya existe → usar Fix B directamente
```

### Bug 7 — ImportError en Python 3.12 con typing
```
Síntoma: ImportError: cannot import name 'list' from 'typing'
Causa:   from typing import list  ← inválido en Python 3.9+
         list es un built-in genérico desde Python 3.9
Fix:     Eliminar la línea — usar list directamente como tipo
Lección: En Python 3.9+: list[str], dict[str, int], etc.
         Ya no necesitas from typing import List, Dict, etc.
```

### Bug 8 — API no recibía variables de TimescaleDB
```
Síntoma: API no conectaba a TimescaleDB
Causa:   docker-compose.yml pasaba DATABASE_URL hardcodeado
         pero config.py construye la URL desde variables
         individuales: TIMESCALE_USER, TIMESCALE_PASSWORD, TIMESCALE_DB
Fix:     Pasar las 3 variables individuales en el bloque env del api
         También faltaba TELEGRAM_CHAT_ID
```

### Bug 9 — Device EUI case mismatch
```
Síntoma: mqtt.unknown_device aunque el device estaba registrado
Causa:   MQTT client normaliza EUI a mayúsculas (.upper())
         pero el endpoint POST guardaba el EUI como llegaba
         Resultado: "a840411d3181bd6b" en DB vs "A840411D3181BD6B" en MQTT
Fix:     Agregar data.device_eui = data.device_eui.upper()
         en el endpoint POST /api/v1/devices/
         antes de buscar si existe y antes de crear
Lección: Normalizar inputs en el punto de entrada siempre
```

### Bug 10 — Credenciales ChirpStack vs .env
```
Síntoma: password authentication failed for user "chirpstack"
Causa:   chirpstack.toml tenía credenciales hardcodeadas "chirpstack:chirpstack"
         pero el .env tenía credenciales diferentes
Fix temporal: Igualar .env a las credenciales del toml
Fix permanente: Usar POSTGRESQL__DSN env var en docker-compose.yml
Lección: Definir UN solo lugar para las credenciales
         y referenciarlas desde todos los demás
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

### Recrear con volumen limpio (datos frescos)
```bash
docker compose stop servicio
docker compose rm -f servicio
docker volume rm aquaalert-platform_nombre_data
docker compose up -d servicio
```

### init.sql solo corre cuando el volumen NO existe
```bash
# Si ya existe el volumen y necesitas re-ejecutar init.sql:
docker volume rm aquaalert-platform_postgres_data
docker compose up -d postgres
# O ejecutar el SQL manualmente:
docker compose exec postgres psql -U usuario -d db -c "SQL aquí"
```

### Warning "version is obsolete" en docker-compose.yml
```yaml
# Eliminar la primera línea del docker-compose.yml:
version: '3.8'   ← borrar esto

# Docker Compose v2 ya no requiere esta línea
# Es cosmético pero genera warning en cada comando
```

---

## ☁️ Azure VM — Reglas de uso

```
✅ git clone (una sola vez)
✅ git pull origin main (para actualizar)
✅ docker compose up/down/logs/ps
✅ docker compose exec (para diagnóstico)
❌ git checkout -b (nunca crear ramas aquí)
❌ git commit (nunca commitear desde Azure)
❌ git push (nunca pushear desde Azure)

Regla: Azure es servidor, laptop es desarrollo
```

### Acceso a ChirpStack con credenciales default
```
ChirpStack UI → http://<IP>:8080
Usuario: admin
Password: admin
⚠️ Cambiar en producción real
```

### Puertos a abrir en Azure NSG
```
8080/TCP → ChirpStack UI
8000/TCP → FastAPI (Swagger en /docs)
3000/TCP → Grafana
1883/TCP → MQTT (si necesitas acceso externo)
1700/UDP → LoRaWAN Gateway Bridge (para Dragino)
```

---

## 🌐 Configuración del Ruleset (GitHub)

```
Settings → Rules → Rulesets → Edit

Enforcement status:  Active ✅
Target branches:     Include default branch ✅

Protections activas:
  ✅ Require a pull request before merging (approvals: 0)
  ✅ Require linear history
  ✅ Require status checks: test-api
  ❌ Todo lo demás
```

---

## 📦 Historial de ramas — Progreso completo

### ✅ Fase 1 — Base del proyecto
```
✅ chore/infra-base           → mosquitto, postgres, nginx, .env, README
✅ chore/docker-compose       → docker-compose.yml completo (9 servicios)
✅ feat/api-core              → requirements, Dockerfile, config, database
✅ feat/sensor-models         → SensorReading y Device ORM (TimescaleDB)
✅ feat/rest-endpoints        → routers sensors y devices (CRUD completo)
✅ feat/node-simulator        → simulador CubeCell + JSN-SR04T via MQTT
✅ chore/grafana-provisioning → datasources y dashboards auto-provisioned
✅ test/decoder-unit-tests    → tests unitarios del decoder con pytest
✅ docs/readme-badges         → badges CI, license, LoRaWAN, Jalisco 🇲🇽
✅ docs/git-workflow-guide    → esta guía en docs/FLUJO-TRABAJO-GIT.md
```

### ✅ Fase 2 — Lógica de negocio
```
✅ feat/fastapi-main          → main.py: lifespan, CORS, routers, /health
✅ feat/mqtt-services         → decoder.py + alert_service.py + mqtt_client.py
✅ chore/chirpstack-cfg       → chirpstack.toml: PostgreSQL, Redis, US915, MQTT
✅ ci/github-actions          → ci.yml real (pytest + ruff + docker build)
                                deploy.yml (SSH deploy a VPS)
```

### ✅ Fixes aplicados (bugs encontrados en proceso)
```
✅ fix/ci-requirements-conflict    → paho-mqtt conflicto de versiones
✅ fix/test-battery-pct-rounding   → assert 67 == 66 corregido
✅ fix/ruff-e712-sensors           → Device.is_active.is_(True)
✅ fix/docker-compose-env-vars     → TIMESCALE vars + TELEGRAM_CHAT_ID
✅ fix/chirpstack-toml-syntax      → [[integration]] → [integration]
✅ fix/chirpstack-postgres-setup   → pg_trgm extension + DSN env vars
✅ fix/chirpstack-env-dsn          → POSTGRESQL__DSN override
✅ fix/config-typing-import        → from typing import list → eliminado
✅ fix/device-eui-normalize        → .upper() en registro de devices
```

### 🔜 Fase 3 — Dashboards y hardware real
```
🔜 feat/grafana-dashboard     → panels nivel agua, batería, alertas
🔜 chore/remove-version-key   → eliminar "version: 3.8" del compose
🔜 chore/securize-credentials → credenciales ChirpStack via env vars
🔜 conectar gateway Dragino   → UDP 1700 → ChirpStack real
🔜 conectar CubeCell físico   → primer uplink hardware end-to-end
🔜 test alertas Telegram      → simular escenario CRITICAL
```

---

## 🏗️ Arquitectura del stack

```
Nodo CubeCell AB02 + JSN-SR04T
    ↓ LoRaWAN 915MHz (US915 sub-band 0)
Gateway Dragino DLOS8N
    ↓ UDP :1700
ChirpStack Gateway Bridge :1700
    ↓ MQTT → mosquitto:1883
ChirpStack v4 Network Server :8080
    ↓ MQTT topic: application/+/device/+/event/up
FastAPI mqtt_client.py
    ├── decoder.py       → bytes → distance_cm, battery_pct
    ├── alert_service.py → fill_pct → NORMAL/WATCH/WARNING/CRITICAL
    │                      → Telegram Bot notificaciones
    └── TimescaleDB      → SensorReading hypertable
         ↓
      Grafana :3000      → dashboards tiempo real
      /docs   :8000      → Swagger UI

Simulador (sin hardware):
  node_simulator.py → MQTT → mismo pipeline ↑
```

---

## 🔑 Acceso a servicios (Azure VM)

```
http://<IP-AZURE>:8000/docs  → FastAPI Swagger UI
http://<IP-AZURE>:8000/health → {"status":"ok","version":"0.1.0"}
http://<IP-AZURE>:8080        → ChirpStack UI (admin/admin)
http://<IP-AZURE>:3000        → Grafana (admin/<GRAFANA_PASSWORD>)
```

---

## 📊 Verificación del pipeline end-to-end

```bash
# 1. Ver lecturas en tiempo real (API)
curl -s http://localhost:8000/api/v1/sensors/A840411D3181BD6B/latest \
  | python3 -m json.tool

# 2. Ver historial (última hora)
curl -s "http://localhost:8000/api/v1/sensors/A840411D3181BD6B/readings?hours=1" \
  | python3 -m json.tool

# 3. Ver lecturas directamente en TimescaleDB
docker compose exec timescaledb psql -U aquaalert -d aquaalert_ts \
  -c "SELECT time, distance_cm, water_level_cm, fill_pct, alert_level
      FROM sensor_readings ORDER BY time DESC LIMIT 5;"

# 4. Ver logs del pipeline completo
docker compose logs --tail=10 api
docker compose logs --tail=10 node-simulator

# 5. Ver estado de todos los servicios
docker compose ps
```

---

*Proyecto: AquaAlert IoT Platform*
*Stack: LoRaWAN + ChirpStack v4 + FastAPI + TimescaleDB + Grafana*
*Hardware: Heltec CubeCell AB02 + JSN-SR04T + Dragino DLOS8N*
*CI/CD: GitHub Actions + Docker Compose*
*Infraestructura: Azure VM Ubuntu + Docker*
*Desarrollado en Guadalajara, Jalisco, México 🇲🇽*
