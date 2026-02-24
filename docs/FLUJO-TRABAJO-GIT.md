# 📋 AquaAlert — Guía de Referencia Git & GitHub
> Lecciones aprendidas en el proceso de desarrollo

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

# ── 6. Mergear PR ← PASO MÁS IMPORTANTE, NO OLVIDAR ──
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
  feat(api): add water level endpoint
  feat(decoder): implement JSN-SR04T payload parser
  feat(mqtt): add async MQTT client for ChirpStack uplinks
  feat(alerts): add threshold evaluation and Telegram notifications
  fix(mqtt): reconnect on broker timeout
  chore(docker): add timescaledb service
  docs(readme): add status badges
  test(decoder): add battery percentage edge cases
  ci: add pytest step to workflow
```

---

## 🏷️ Nomenclatura de ramas

```
feat/fastapi-main
feat/mqtt-services
feat/sensor-models
feat/payload-decoder
feat/node-simulator
fix/mqtt-reconnect-timeout
chore/chirpstack-config
chore/grafana-provisioning
chore/docker-compose-stack
ci/github-actions-pipeline
docs/readme-badges
docs/git-workflow-guide
test/decoder-unit-tests
```

---

## 🔒 Branch Protection — Situaciones especiales

### Cuando el merge falla por reglas del ruleset:
```bash
# Error que verás:
# "Pull request is not mergeable: the base branch policy prohibits the merge"

# Opción A — Esperar que el CI pase:
gh pr checks N
gh pr merge N --squash --delete-branch

# Opción B — Merge como administrador (cuando CI es placeholder):
gh pr merge N --squash --delete-branch --admin
# ✅ Usar mientras el CI real no está implementado

# Opción C — Auto-merge cuando pasen los checks:
gh pr merge N --squash --delete-branch --auto
```

### Cuándo usar --admin:
```
✅ CI todavía es placeholder (no tiene tests reales)
✅ Eres el único desarrollador
✅ Sabes que el código está correcto manualmente
❌ NO usar cuando el CI real con pytest ya esté activo
```

### Cuándo ya NO necesitarás --admin:
```
Cuando ci/github-actions esté implementado con:
  - pytest corriendo tests reales
  - El Ruleset tenga "Require status checks: test-api"
  Entonces el CI valida automáticamente y --admin
  ya no es necesario
```

---

## ⚠️ Errores comunes y soluciones

### Error: "no se puede pull con rebase: tienes cambios sin marcar"
```bash
# Causa: intentaste cambiar de rama con archivos modificados sin commit
# Solución A (si los cambios van en esta rama):
git add . && git commit -m "tipo: descripción"
git checkout main

# Solución B (guardar temporalmente):
git stash push -m "descripción del WIP"
git checkout main
# Cuando regreses:
git checkout mi-rama && git stash pop
```

### Error: "rama adelantada a origin/main por 1 commit"
```bash
# Causa: tienes commits locales sin pushear
git push origin main
```

### Error: "rama detrás de origin/main por 1 commit"
```bash
# Causa: origin tiene cambios que no tienes local
git pull origin main
```

### Warning: "borrando rama que aún no ha sido fusionada a HEAD"
```bash
# SEÑAL DE ALERTA: el PR no fue mergeado todavía
# Solución: mergear ANTES de borrar
gh pr merge N --squash --delete-branch
# Luego sí borrar:
git branch -d nombre-rama
```

### Error: "Permiso denegado" al editar archivos del proyecto
```bash
# Causa: archivos creados con sudo
ls -la .github/workflows/
# Si ves "root root" como dueño:
sudo chown -R $USER:$USER ~/Github/aquaalert-platform/
# Regla: NUNCA usar sudo con git o archivos del proyecto
```

### Error: "GH006/GH013 Protected branch update failed"
```bash
# Causa: push directo a main con branch protection activa
# Eso es correcto → la protección funciona ✅
# Solución: revertir commit local y usar rama + PR
git reset --hard HEAD~1
git checkout -b feat/mi-fix
```

---

## 🔍 Comandos de diagnóstico frecuentes

```bash
# Estado del árbol de trabajo (ejecutar SIEMPRE antes de checkout)
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

Agrégala cuando ocurra alguna de estas condiciones:
```
✅ Se une otro desarrollador al proyecto
✅ Tienes clientes pagando y necesitas staging
✅ El proyecto crece a +5 features en paralelo
✅ Necesitas entorno de pruebas separado de producción
```
Por ahora: **main → feat/* → PR → main** es suficiente.

---

## 🌐 Configuración del Ruleset (GitHub)

```
Settings → Rules → Rulesets → Edit

Enforcement status:  Active ✅        ← Disabled = no funciona
Target branches:     Include default branch ✅

Branch protections:
  ✅ Require a pull request before merging
       └─ Required approvals: 0
       └─ Dismiss stale reviews: ✅
  ✅ Require linear history
  ❌ Require status checks  ← activar cuando CI real esté listo
  ❌ Todo lo demás

Nota: repos privados con cuenta Free no aplican las reglas
→ hacer el repo PÚBLICO para que funcionen.
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

## 📦 Historial de ramas — Progreso del proyecto

### ✅ Fase 1 — Base del proyecto (completada)
```
✅ chore/infra-base           → mosquitto, postgres, nginx, .env, README
✅ chore/docker-compose       → docker-compose.yml completo (9 servicios)
✅ feat/api-core              → requirements, Dockerfile, config, database
✅ feat/sensor-models         → SensorReading, Device ORM (TimescaleDB)
✅ feat/rest-endpoints        → routers sensors y devices (CRUD completo)
✅ feat/node-simulator        → simulador CubeCell + JSN-SR04T via MQTT
✅ chore/grafana-provisioning → datasources y dashboards auto-provisioned
✅ test/decoder-unit-tests    → tests unitarios con pytest
✅ docs/readme-badges         → badges CI, license, LoRaWAN, Made in Jalisco
✅ docs/git-workflow-guide    → esta guía en docs/FLUJO-TRABAJO-GIT.md
```

### ✅ Fase 2 — Lógica de negocio (en progreso)
```
✅ feat/fastapi-main     → main.py: lifespan, CORS, routers, /health
✅ feat/mqtt-services    → decoder.py + alert_service.py + mqtt_client.py

🔜 chore/chirpstack-cfg  → chirpstack.toml (config servidor LoRaWAN)
🔜 ci/github-actions     → ci.yml y deploy.yml reales con pytest + SSH deploy
```

### 🔜 Fase 3 — Operación (próxima)
```
🔜 primer docker compose up   → stack completo funcionando local
🔜 conectar gateway Dragino   → UDP 1700 → ChirpStack
🔜 conectar CubeCell físico   → primer uplink real end-to-end
🔜 dashboard Grafana          → panels de nivel y batería
🔜 test alertas Telegram      → simular nivel crítico
```

---

*Proyecto: AquaAlert IoT Platform*
*Stack: LoRaWAN + ChirpStack v4 + FastAPI + TimescaleDB + Grafana*
*Hardware: Heltec CubeCell AB02 + JSN-SR04T + Dragino DLOS8N*
*Desarrollado en Guadalajara, Jalisco, México 🇲🇽*
