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
git checkout main && git pull && git branch -d tipo/nombre-descriptivo
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
  feat(decoder): support JSN-SR04T payload format
  fix(mqtt): reconnect on broker timeout
  chore(docker): add timescaledb service
  docs(readme): add status badges
  test(decoder): add battery percentage edge cases
  ci: add pytest step to workflow
```

---

## 🏷️ Nomenclatura de ramas

```
feat/docker-compose-stack
feat/fastapi-models
feat/mqtt-client
feat/payload-decoder
feat/alert-service-telegram
feat/node-simulator
fix/mqtt-reconnect-timeout
chore/chirpstack-config
chore/grafana-provisioning
ci/github-actions-pipeline
docs/readme-badges
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
  Entonces el CI valida automáticamente y el merge
  funciona normal sin flags especiales
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
# o si estás en una rama:
git push origin nombre-rama
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
# Luego sí:
git branch -d nombre-rama
```

### Error: "Permiso denegado" al editar archivos del proyecto
```bash
# Causa: archivos creados con sudo
ls -la .github/workflows/
# Si ves "root root" como dueño:
sudo chown -R $USER:$USER ~/Github/aquaalert-platform/
# Nunca más usar sudo con git o archivos del proyecto
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
✅ Necesitas un entorno de pruebas separado de producción
```
Por ahora: **main → feat/* → PR → main** es suficiente.

---

## 📦 Orden de ramas completadas

```
✅ chore/infra-base           → mosquitto, postgres, nginx, .env, README
✅ chore/docker-compose       → docker-compose.yml completo
✅ feat/api-core              → requirements, Dockerfile, config, database
✅ feat/sensor-models         → SensorReading, Device ORM
✅ feat/rest-endpoints        → routers sensors y devices
✅ feat/node-simulator        → simulador CubeCell + JSN-SR04T
✅ chore/grafana-provisioning → datasources y dashboards
✅ test/decoder-unit-tests    → tests del decoder
✅ docs/readme-badges         → badges CI, license, LoRaWAN

🔜 feat/fastapi-main          → app/main.py (punto de entrada API)
🔜 feat/mqtt-services         → mqtt_client, decoder, alert_service
🔜 chore/chirpstack-cfg       → chirpstack.toml
🔜 ci/github-actions          → ci.yml y deploy.yml reales con pytest
```

---

## 🌐 Configuración del Ruleset (GitHub)

```
Settings → Rules → Rulesets → Edit

Enforcement status:  Active ✅
Target branches:     Include default branch ✅

Branch protections:
  ✅ Require a pull request before merging
       └─ Required approvals: 0
       └─ Dismiss stale reviews: ✅
  ✅ Require linear history
  ❌ Require status checks  ← activar cuando CI real esté listo
  ❌ Todo lo demás
```

---

*Última actualización: durante setup inicial de aquaalert-platform*
*Stack: LoRaWAN + ChirpStack + FastAPI + TimescaleDB + Grafana*
