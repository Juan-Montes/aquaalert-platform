# 📋 AquaAlert — Guía de Referencia Git & GitHub
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
       └─ Required approvals: 0
       └─ Dismiss stale reviews when new commits pushed: ✅
  ✅ Require linear history
  ✅ Require status checks to pass          ← activar con CI real
       └─ Require branches to be up to date before merging: ✅
       └─ Add checks → buscar: "test-api"
  ❌ Todo lo demás

Nota: repos privados con cuenta Free no aplican las reglas.
Hacer el repo PÚBLICO para que funcionen.
```

### Cómo agregar el check "test-api":
```
1. Ir a Settings → Rules → Rulesets → Edit
2. Marcar "Require status checks to pass"
3. Clic en "+ Add checks"
4. Buscar y seleccionar: test-api
5. Marcar: "Require branches to be up to date before merging"
6. Save changes

⚠️ test-api solo aparece en el buscador después de que
   el CI haya corrido al menos UNA vez en GitHub Actions
```

### Verificar que la protección funciona:
```bash
echo "test" >> README.md
git add . && git commit -m "test: direct push blocked"
git push origin main
# Debe salir: "Changes must be made through a pull request" ✅
git reset --hard HEAD~1   # limpiar el commit de prueba
```

---

## 🔒 Merge — Situaciones especiales

### Cuando el merge falla por reglas del ruleset:
```bash
# Error que verás:
# "Pull request is not mergeable: the base branch policy prohibits the merge"

# Opción A — Esperar que el CI pase y reintentar:
gh pr checks N
gh pr merge N --squash --delete-branch

# Opción B — Merge como administrador (CI placeholder):
gh pr merge N --squash --delete-branch --admin
# ✅ Válido mientras el CI real no está implementado

# Opción C — Auto-merge cuando pasen los checks:
gh pr merge N --squash --delete-branch --auto
```

### Cuándo usar --admin:
```
✅ CI todavía es placeholder (no tiene tests reales)
✅ Eres el único desarrollador
✅ Sabes que el código está correcto
❌ NO usar cuando CI real + status check estén activos
```

### Cuándo ya NO necesitas --admin:
```
Cuando ci/github-actions esté mergeado Y el Ruleset
tenga "Require status checks: test-api" configurado.
El CI valida automáticamente cada PR → merge normal.
```

---

## ⚠️ Errores comunes y soluciones

### "no se puede pull con rebase: tienes cambios sin marcar"
```bash
# Causa: cambiar de rama con archivos modificados sin commit
# Solución A — commit en esta rama:
git add . && git commit -m "tipo: descripción"
git checkout main

# Solución B — guardar temporalmente:
git stash push -m "descripción WIP"
git checkout main
# Al regresar:
git checkout mi-rama && git stash pop
```

### "rama adelantada a origin/main por 1 commit"
```bash
# Causa: commits locales sin pushear
git push origin main
```

### "rama detrás de origin/main por 1 commit"
```bash
# Causa: origin tiene cambios que no tienes local
git pull origin main
```

### Warning: "borrando rama que aún no ha sido fusionada a HEAD"
```bash
# SEÑAL DE ALERTA → el PR NO fue mergeado todavía
# Solución: mergear primero, luego borrar
gh pr merge N --squash --delete-branch
git branch -d nombre-rama
```

### "Permiso denegado" al editar archivos del proyecto
```bash
# Causa: archivos creados con sudo
ls -la .github/workflows/
# Si ves "root root" como dueño:
sudo chown -R $USER:$USER ~/Github/aquaalert-platform/
# Regla: NUNCA usar sudo con git o archivos del proyecto
```

### "GH006/GH013 Protected branch update failed"
```bash
# Causa: push directo a main con protección activa
# La protección está funcionando correctamente ✅
# Solución: revertir y usar rama + PR
git reset --hard HEAD~1
git checkout -b feat/mi-fix
```

---

## 🔍 Comandos de diagnóstico frecuentes

```bash
# Estado del árbol (ejecutar SIEMPRE antes de checkout)
git status

# Historial limpio
git log --oneline -10

# Ver todas las ramas (local + remoto)
git branch -a

# Ver PRs abiertos
gh pr list

# Ver estado del CI en un PR
gh pr checks N

# Ver diferencias antes de commitear
git diff

# Limpiar ramas locales ya mergeadas
git fetch --prune
git branch --merged main | grep -v "main" | xargs git branch -d
```

---

## 🚀 Cuándo agregar rama "develop"

```
✅ Se une otro desarrollador al proyecto
✅ Tienes clientes pagando y necesitas staging
✅ El proyecto crece a +5 features en paralelo
✅ Necesitas entorno de pruebas separado de producción

Por ahora: main → feat/* → PR → main es suficiente
```

---

## 📦 Historial de ramas — Progreso del proyecto

### ✅ Fase 1 — Base del proyecto (completada)
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

### ✅ Fase 2 — Lógica de negocio (completada)
```
✅ feat/fastapi-main     → main.py: lifespan, CORS, routers, /health
✅ feat/mqtt-services    → decoder.py + alert_service.py + mqtt_client.py
✅ chore/chirpstack-cfg  → chirpstack.toml: PostgreSQL, Redis, US915, MQTT
✅ ci/github-actions     → ci.yml real (pytest + ruff + docker build)
                           deploy.yml (SSH deploy a VPS)
```

### 🔜 Fase 3 — Primer arranque (siguiente)
```
🔜 docker compose up     → stack completo funcionando local
🔜 ChirpStack UI         → registrar gateway Dragino DLOS8N
🔜 CubeCell físico       → primer uplink real end-to-end
🔜 Grafana dashboards    → panels nivel de agua y batería
🔜 Test Telegram         → simular escenario CRITICAL
🔜 Activar status check  → agregar test-api al Ruleset
```

---

## 🏗️ Arquitectura del stack

```
Nodo CubeCell AB02 + JSN-SR04T
    ↓ LoRaWAN 915MHz
Gateway Dragino DLOS8N
    ↓ UDP :1700
ChirpStack v4 (Network Server)
    ↓ MQTT → mosquitto:1883
    topic: application/+/device/+/event/up
FastAPI (mqtt_client.py)
    ├── decoder.py       → bytes → distance_cm, battery_pct
    ├── alert_service.py → fill_pct → NORMAL/WATCH/WARNING/CRITICAL
    └── TimescaleDB      → SensorReading hypertable
         ↓
      Grafana :3000      → dashboards tiempo real
      Telegram Bot       → alertas push al celular
```

---

*Stack: LoRaWAN + ChirpStack v4 + FastAPI + TimescaleDB + Grafana*
*Hardware: Heltec CubeCell AB02 + JSN-SR04T + Dragino DLOS8N*
*Desarrollado en Guadalajara, Jalisco, México 🇲🇽*
