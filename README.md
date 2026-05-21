# SRE Monitoring Suite

![Tests](https://github.com/Iriome-Santana/sre-monitoring-suite/actions/workflows/tests.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)

Sistema de monitoreo local desarrollado en Python para supervisar uso de CPU, memoria RAM y disco, con alertas automáticas, gestión de estado para evitar alertas repetidas, tests automatizados con GitHub Actions, métricas conectadas a Prometheus, visualización en Grafana y logs centralizados en Loki.

Proyecto orientado a prácticas reales de Site Reliability Engineering: observabilidad, alerting, automatización y respuesta a incidentes.

---

## Table of Contents

- [What is this?](#what-is-this)
- [Features](#features)
- [Architecture](#architecture)
- [Observability Stack](#observability-stack)
- [State Management](#state-management)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Automation (cron)](#automation-cron)
- [Daily Report](#daily-report)
- [Architecture Decision Records](#architecture-decision-records)
- [Production Readiness Gap Analysis](#production-readiness-gap-analysis)
- [Further Documentation](#further-documentation)

---

## What is this?

En muchos sistemas pequeños o personales no existe monitoreo básico. Los problemas — disco lleno, CPU saturada, fuga de memoria — se detectan cuando el sistema ya está degradado o caído.

Este proyecto busca detectar problemas de recursos antes del fallo, evitar alertas repetidas (alert fatigue), enviar notificaciones claras y accionables, y automatizar la supervisión con herramientas simples.

No pretende reemplazar soluciones como Prometheus o Datadog. Fue diseñado para entender cómo funciona el monitoreo desde cero, implementar alerting sin dependencias externas, practicar gestión de estado y simular responsabilidades reales de SRE en entornos pequeños.

---

## Features

- Monitoreo de CPU basado en idle time (`top`)
- Monitoreo de memoria usando memoria disponible real (`free`)
- Monitoreo de uso de disco por path configurable (`df`)
- Umbrales configurables vía variables de entorno
- Gestión de estado para detectar cambios (OK → WARNING → CRITICAL)
- Alertas y recoveries enviados a Discord
- Logs detallados por cada ejecución en formato JSON estructurado
- Logs centralizados en Loki con filtrado por componente y nivel
- Reporte diario agregado
- Limpieza automática de logs antiguos
- Tests automatizados con pytest y GitHub Actions (91% de cobertura)
- Métricas expuestas para Prometheus + dashboards en Grafana

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CRON SCHEDULER                           │
│                  (Cada 5 minutos)                           │
└────────────────┬────────────┬────────────┬─────────────────┘
                 │            │            │
                 ▼            ▼            ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │disk_check  │ │memory_check│ │ cpu_check  │
        │   .py      │ │   .py      │ │   .py      │
        └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌────────────────┐
                    │  notifier.py   │
                    │  (send_alert)  │
                    └────────┬───────┘
                             │
                    ┌────────▼────────┐
                    │ Discord Webhook │
                    │  (POST request) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Discord Server │
                    │ #alertas-sistema│
                    └─────────────────┘
```

### Componentes

**disk_check.py** — Lee uso de disco con `df -h`, compara contra thresholds, detecta cambios de estado y alerta si es necesario.

**memory_check.py** — Lee memoria con `free -m`, calcula % disponible, aplica state management y envía alertas de memoria baja.

**cpu_check.py** — Lee CPU con `top -bn1`, extrae % idle con regex, detecta sobrecarga y alerta en cambios.

**notifier.py** — Clase `Notifier` con `send_discord()` y `send_alert()`. Construye embeds con colores según severidad (azul, amarillo, rojo) y timestamps UTC.

**base_check.py** — Módulo base con patrón Template Method. Centraliza la lógica común de state management y logging. Cada check hereda de aquí.

### Flujo de una alerta

```
1. Cron ejecuta disk_check.py
2. Script lee uso actual: 85%
3. Lee last_state desde /tmp/disk.state: "OK"
4. Determina current_state: "WARNING" (85% > 80%)
5. Detecta cambio: "OK" → "WARNING"
6. Llama send_alert(title, message, level="WARNING")
7. notifier.py construye embed JSON
8. POST a Discord webhook
9. Discord muestra alerta amarilla ⚠️
10. Guarda nuevo state: "WARNING" en /tmp/disk.state
11. Exit code 1 (WARNING)
```

---

## Observability Stack

```
┌──────────────────┐
│ metrics_exporter │  → Recolecta métricas del sistema cada 15s
└────────┬─────────┘
         │ HTTP :8000/metrics
         ▼
┌──────────────────┐
│   Prometheus     │  → Almacena time-series data
└────────┬─────────┘
         │ PromQL queries
         ▼
┌──────────────────┐
│     Grafana      │  → Visualización en dashboards y logs
└──────────────────┘
         ▲
         │ LogQL queries
┌────────┴─────────┐
│      Loki        │  → Almacena y indexa logs por labels
└────────▲─────────┘
         │ push logs
┌────────┴─────────┐
│    Promtail      │  → Lee archivos de log y los envía a Loki
└────────▲─────────┘
         │ lee
~/sre-monitoring-suite/logs/*.log
```

### Servicios

| Servicio | Puerto | Qué hace |
|---|---|---|
| metrics_exporter | 8000 | Expone métricas del sistema para Prometheus |
| Prometheus | 9090 | Almacena métricas en series temporales |
| Grafana | 3000 | Dashboards de métricas y panel de logs |
| Loki | 3100 | Almacena y indexa logs por labels |
| Promtail | 9080 | Agente que lee logs y los envía a Loki |

### Métricas disponibles

| Métrica | Descripción |
|---|---|
| `sre_disk_usage_percent` | Uso de disco en porcentaje |
| `sre_memory_available_percent` | Memoria disponible en porcentaje |
| `sre_cpu_idle_percent` | CPU idle en porcentaje |

### Dashboard

El dashboard incluye gráfico de línea de uso de disco con tendencia temporal, gauge de memoria disponible con thresholds de color (rojo < 20%, amarillo 20-40%, verde > 40%), gráfico de línea de CPU idle, y panel de logs centralizados de todos los componentes.

![Grafana Dashboard](docs/dashboard_monitoring.png)

Ver [docs/GRAFANA.md](docs/GRAFANA.md) para instrucciones de importación del dashboard.

### LogQL queries de ejemplo

| Query | Resultado |
|---|---|
| `{job="sre-monitoring-suite"}` | Todos los logs |
| `{job="sre-monitoring-suite", component="disk"}` | Solo logs de disk_check |
| `{job="sre-monitoring-suite", component="cpu"}` | Solo logs de cpu_check |
| `{job="sre-monitoring-suite", level="ERROR"}` | Solo errores |
| `{job="sre-monitoring-suite"} \|= "Estado actual"` | Cambios de estado |
| `{job="sre-monitoring-suite"} \| json \| level != "INFO"` | Warnings y críticos |

---

## State Management

Cada check guarda su último estado en un archivo en `/tmp`:

```
/tmp/
├── disk.state     →  "OK" | "WARNING" | "CRITICAL"
├── memory.state   →  "OK" | "WARNING" | "CRITICAL"
└── cpu.state      →  "OK" | "WARNING" | "CRITICAL"
```

**Lógica de alertas:**
- **Alerta:** `last_state != current_state AND current_state != "OK"`
- **Recovery:** `last_state != "OK" AND current_state == "OK"`

Sin estado, cada ejecución de cron generaría una alerta aunque nada hubiera cambiado. El state management es lo que separa un sistema de alerting real de un script que simplemente comprueba umbrales.

Los archivos en `/tmp` se borran en cada reboot, lo cual es intencionado: el sistema arranca con un estado limpio (OK), sin arrastrar alertas de sesiones anteriores.

---

## Quick Start

```bash
git clone https://github.com/Iriome-Santana/sre-monitoring-suite.git
cd sre-monitoring-suite
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copiar y configurar variables de entorno:

```bash
cp .env.example .env
# Editar .env con tus valores
```

Ejecutar un check manualmente:

```bash
python src/cpu_check.py
python src/memory_check.py
python src/disk_check.py
```

Iniciar el stack de observabilidad completo:

```bash
# Iniciar exporter de métricas
python3 src/metrics_exporter.py &

# Iniciar Prometheus, Grafana, Loki y Promtail
docker compose up -d

# Servicios disponibles:
# Métricas raw:   http://localhost:8000/metrics
# Prometheus UI:  http://localhost:9090
# Grafana:        http://localhost:3000  (admin/admin)
# Loki:           http://localhost:3100
```

---

## Configuration

Variables de entorno que controlan el comportamiento:

| Variable | Descripción |
|---|---|
| `WARNING` | Umbral de warning (porcentaje) |
| `CRITICAL` | Umbral crítico (porcentaje) |
| `DISCORD_WEBHOOK` | URL del webhook de Discord |
| `DISK_PATH` | Path a monitorear (por defecto `/`) |
| `NOTIFICATIONS_ENABLED` | `true` / `false` |
| `METRICS_PORT` | Puerto del exporter de métricas |
| `SCRAPE_INTERVAL` | Intervalo de scraping en segundos |

---

## Automation (cron)

Ejecutar cada 5 minutos con rutas absolutas (requerido para cron):

```bash
*/5 * * * * python3 /ruta/absoluta/src/cpu_check.py    >> ~/sre/logs/cpu_check.log 2>&1
*/5 * * * * python3 /ruta/absoluta/src/memory_check.py >> ~/sre/logs/memory_check.log 2>&1
*/5 * * * * python3 /ruta/absoluta/src/disk_check.py   >> ~/sre/logs/disk_check.log 2>&1
```

> **Nota:** Cron ejecuta con un directorio de trabajo diferente al shell interactivo. Las rutas relativas no funcionan. Ver [docs/troubleshooting.md](docs/troubleshooting.md#problem-1-cron-no-ejecutaba-los-scripts) para más detalle.

---

## Daily Report

El script `daily_report.sh` genera un resumen diario con métricas agregadas a partir de los logs. Configurar en cron para ejecución diaria:

```bash
0 8 * * * /ruta/absoluta/scripts/daily_report.sh >> ~/sre/logs/daily_report.log 2>&1
```

---

## Architecture Decision Records

### Por qué 3 scripts separados en lugar de 1 script unificado

La alternativa era un único `base_check.py --check disk`. Elegí 3 scripts independientes con un módulo base compartido porque en SRE real se prioriza la observabilidad sobre la compacidad. Si `memory_check` falla, quiero saber exactamente cuál falló sin parsear logs mezclados. Además, permite scheduling independiente: `disk_check` cada 5 minutos, `cpu_check` cada 1 minuto si fuera necesario. Este patrón está presente en Datadog agents, Nagios plugins y Prometheus exporters.

### Por qué state files en /tmp en lugar de base de datos

Para detectar cambios de estado no necesito histórico. SQLite sería overkill y añadiría una dependencia que puede corromperse. Los archivos en `/tmp` son simples, rápidos, sin dependencias, y se limpian solos en cada reboot — lo cual es un feature, no un bug. Si necesitara análisis de tendencias, migraría a Prometheus, que es la herramienta correcta para eso. YAGNI principle.

### Por qué Discord en lugar de PagerDuty

PagerDuty tiene escalation policies y on-call scheduling, pero cuesta dinero y es overkill para un proyecto de aprendizaje individual. Discord da el 80% de lo que necesito (notificaciones en tiempo real, móvil y desktop) con el 5% del esfuerzo. El código está diseñado para que la migración sea trivial cuando sea necesario: un único punto de cambio en `notifier.py`.

### Por qué cron en lugar de systemd timers

Más simple, familiar y funciona en cualquier Linux sin configuración adicional. La mejora natural sería migrar a systemd timers para mejor logging y control de dependencias entre servicios, pero para este caso de uso cron es suficiente.

### Por qué idle CPU en lugar de load average

El idle time refleja directamente la capacidad disponible y es directamente interpretable como porcentaje para alerting. Load average requiere normalizar por número de cores para ser útil, añadiendo complejidad sin beneficio para este caso.

### Por qué variables de entorno para configuración

Siguiendo el principio 12-factor: la configuración que varía entre entornos no debe estar en el código. Los umbrales pueden ser distintos en un servidor de desarrollo y en uno de producción sin tocar una línea de Python.

### Por qué Loki en lugar de ELK Stack

Elasticsearch + Logstash + Kibana es la solución estándar de mercado para centralización de logs, pero consume recursos significativos y requiere configuración compleja. Loki indexa solo los labels (component, level, job), no el contenido completo de los logs — lo que lo hace extremadamente ligero. Para este caso de uso, donde los logs ya son JSON estructurado y los filtros naturales son por componente y nivel, Loki es la herramienta correcta. ELK tendría sentido si necesitara full-text search sobre el contenido de los mensajes.

### Por qué Promtail en lugar de Fluentd o Logstash

Promtail es el agente nativo de Loki — misma organización, mismo modelo de datos, configuración mínima. Fluentd y Logstash son más potentes pero añaden complejidad sin beneficio aquí. El pipeline_stages de Promtail es suficiente para parsear el JSON y extraer labels.

---

## Production Readiness Gap Analysis

Este proyecto es educacional. Aquí está lo que cambiaría para producción real.

### ✅ Lo que ya está production-ready

State management que evita alertas duplicadas, exit codes que siguen estándares de monitoreo, logging estructurado con timestamps, separación de concerns que facilita el mantenimiento, métricas históricas con dashboards visuales, y logs centralizados con filtrado por componente y nivel.

### ⚠️ Lo que falta y cómo priorizarlo

**Must-have (1-2 días):**
El webhook de Discord está en un archivo de configuración plano. En producción iría a AWS Secrets Manager o HashiCorp Vault. El sistema tampoco tiene deadman's switch: si el propio monitor falla, nadie lo sabe. Un cron job cada 10 minutos que haga ping a healthchecks.io resuelve esto.

**Nice-to-have (1 semana):**
Runbooks documentados para cada tipo de alerta. Alertas en Grafana basadas en queries de Loki para notificar cuando aparecen ERRORs en los logs.

**Futuro (1 mes+):**
Soporte multi-servidor (agente por servidor + collector central), dashboard web, integración con PagerDuty para on-call real.

**Por qué este orden:** los secrets son una vulnerabilidad de seguridad obvia; el deadman's switch responde a la pregunta "¿quién vigila al vigilante?". Ambos son críticos antes que cualquier feature nuevo.

---

## Further Documentation

| Documento | Contenido |
|---|---|
| [docs/troubleshooting.md](docs/troubleshooting.md) | Problemas reales encontrados durante el desarrollo, proceso de debugging paso a paso y metodología de resolución |
| [docs/GRAFANA.md](docs/GRAFANA.md) | Instrucciones para importar el dashboard y configurar los data sources |
| [docs/TESTING.md](docs/TESTING.md) | Checklist de verificación del stack completo e integration tests |

---

## Author

Built by **Iriome Santana** as part of a self-taught journey into Site Reliability Engineering and DevOps.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Iriome%20Santana-0077B5?logo=linkedin)](https://www.linkedin.com/in/iriome-santana-socorro)

> 💬 **Feedback welcome.** Si también estás aprendiendo SRE/DevOps y quieres discutir las decisiones de arquitectura, abre un issue o escríbeme en LinkedIn.