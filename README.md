# SRE Monitoring Suite (Python)

Sistema de monitoreo local desarrollado en Python para supervisar
uso de CPU, memoria RAM y disco, con alertas automáticas y
gestión de estado para evitar alertas repetidas.

Proyecto orientado a prácticas reales de Site Reliability Engineering:
observabilidad, alerting, automatización y respuesta a incidentes.

## Problem Statement

En muchos sistemas pequeños o personales no existe monitoreo básico.
Los problemas (disco lleno, CPU saturada, fuga de memoria) se detectan
cuando el sistema ya está degradado o caído.

Este proyecto busca:
- Detectar problemas de recursos antes del fallo
- Evitar alertas repetidas (alert fatigue)
- Enviar notificaciones claras y accionables
- Automatizar la supervisión con herramientas simples

## Features

- Monitoreo de CPU basado en idle time (top)
- Monitoreo de memoria usando memoria disponible real (free)
- Monitoreo de uso de disco por path configurable (df)
- Umbrales configurables vía variables de entorno
- Gestión de estado para detectar cambios (OK → WARNING → CRITICAL)
- Alertas y recoveries enviados a Discord
- Logs detallados por cada ejecución
- Scripts de testing manual
- Reporte diario agregado
- Limpieza automática de logs antiguos

## Architecture

Cada check funciona de manera independiente:

check.py
  ├── Recolecta métricas del sistema
  ├── Evalúa umbrales
  ├── Compara con el último estado
  ├── Decide si alertar o recuperar
  ├── Envía notificación
  └── Guarda el nuevo estado

El módulo notifier abstrae el envío de alertas
y permite añadir nuevos canales fácilmente.

## When to use this

- Sistemas pequeños
- Servidores personales
- Laboratorios
- Entornos sin herramientas de monitoreo dedicadas


## Installation

```bash
git clone https://github.com/tuusuario/sre-monitoring-suite.git
cd sre-monitoring-suite
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


---

## 🔧 Configuration (MUY IMPORTANTE)

```md
## Configuration

Las siguientes variables de entorno controlan el comportamiento:

- WARNING: umbral de warning
- CRITICAL: umbral crítico
- DISCORD_WEBHOOK: webhook de Discord
- DISK_PATH: path a monitorear (por defecto /)
- NOTIFICATIONS_ENABLED: true/false

## Run manually

```bash
python src/cpu_check.py
python src/memory_check.py
python src/disk_check.py


---

## ⏱️ Automation (CRON)

```md
## Automation (cron)

Ejecutar cada 5 minutos:

```bash
*/5 * * * * python3 /path/src/cpu_check.py >> ~/sre/logs/cpu_check.log 2>&1


---

## 📊 Daily Report

```md
## Daily Report

El script `daily_report.sh` genera un resumen diario
con métricas agregadas a partir de los logs.
