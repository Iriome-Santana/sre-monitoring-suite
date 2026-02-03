#!/usr/bin/env python3
"""
Script de monitoreo de uso de disco.
Autor: Iriome
Fecha: 02/02/2026
"""

import subprocess
import sys
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Leer configuración
DISK_PATH = os.environ.get("DISK_PATH", "/")
WARNING_THRESHOLD = os.environ.get("WARNING", "80")
CRITICAL_THRESHOLD = os.environ.get("CRITICAL", "90")

try:
    warning_threshold = int(WARNING_THRESHOLD)
    critical_threshold = int(CRITICAL_THRESHOLD)
except ValueError:
    logging.error("Los umbrales deben ser números enteros")
    sys.exit(2)

if warning_threshold >= critical_threshold:
    logging.error("WARNING debe ser menor que CRITICAL")
    sys.exit(2)

logging.info(
    f"Chequeando disco en '{DISK_PATH}' "
    f"(warning={warning_threshold}%, critical={critical_threshold}%)"
)

result = subprocess.run(
    ["df", "-h", DISK_PATH],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    logging.error("Fallo al ejecutar df")
    logging.error(result.stderr.strip())
    sys.exit(2)

lines = result.stdout.splitlines()

if len(lines) < 2:
    logging.error("Salida inesperada de df")
    sys.exit(2)

parts = lines[1].split()

if len(parts) < 5:
    logging.error("No se pudo extraer Use%")
    sys.exit(2)

use_percent_str = parts[4]

try:
    use_percent = int(use_percent_str.strip('%'))
except ValueError:
    logging.error(f"Valor inválido de uso de disco: {use_percent_str}")
    sys.exit(2)

if use_percent < warning_threshold:
    logging.info(f"OK - Uso de disco: {use_percent}%")
    sys.exit(0)
elif use_percent < critical_threshold:
    message = f"Uso de disco en {DISK_PATH}: {use_percent}%"
    logging.warning(f"WARNING - {message}")
    
    send_alert(
        title= "ADVERTENCIA de Disco",
        message= message,
        level= "WARNING"
    )
    sys.exit(1)

else:
    message = f"Uso de disco en {DISK_PATH}: {use_percent}%"
    logging.error(f"CRITICAL - {message}")
    
    # Enviar alerta
    send_alert(
        title="CRÍTICO: Disco Lleno",
        message=message,
        level="CRITICAL"
    )
    sys.exit(2)
