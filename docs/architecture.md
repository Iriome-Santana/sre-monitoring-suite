# Architecture Overview

Este proyecto implementa un sistema de monitoreo local
basado en checks independientes ejecutados de forma periódica.

La arquitectura prioriza:
- Simplicidad
- Bajo acoplamiento
- Fácil extensión
- Claridad operativa

## Components

### 1. Resource Checks
Cada recurso del sistema se monitorea mediante un script independiente:

- cpu_check.py
- memory_check.py
- disk_check.py

Cada check sigue el mismo patrón:
1. Recolección de métricas del sistema
2. Evaluación contra umbrales
3. Determinación del estado (OK / WARNING / CRITICAL)
4. Comparación con el estado anterior
5. Decisión de alertar o no
6. Persistencia del nuevo estado

## Execution Flow

[CRON]
   ↓
check.py
   ↓
Recolectar métricas (top / free / df)
   ↓
Calcular porcentaje relevante
   ↓
Evaluar umbrales
   ↓
Leer último estado (/tmp/*.state)
   ↓
Comparar estados
   ↓
¿Cambio de estado?
   ├─ Sí → Enviar alerta o recovery
   └─ No → No hacer nada
   ↓
Guardar estado actual
   ↓
Exit code estándar (0 / 1 / 2)

## State Management

El sistema utiliza archivos de estado locales
para persistir el último estado de cada check.

Ubicación:
/tmp/<check_name>.state

Estados posibles:
- OK
- WARNING
- CRITICAL

Este enfoque permite:
- Evitar alertas repetidas
- Detectar recuperaciones
- Mantener el sistema stateless en memoria

## Alerting System

Las alertas se gestionan mediante el módulo notifier.

Características:
- Abstracción del canal de notificación
- Soporte actual para Discord
- Diseño extensible para futuros canales

El sistema envía alertas únicamente cuando:
- El estado cambia
- El estado no es OK

## Design Principles

- Fail fast: errores críticos finalizan la ejecución
- Single responsibility: un recurso por check
- Configuración externa al código
- Evitar dependencias pesadas
- Observabilidad sobre complejidad
