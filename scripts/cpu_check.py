#!/usr/bin/env python3
"""
Script de monitoreo de uso de CPU.
Autor: Iriome
Fecha: 02/02/2026
"""

import subprocess
import sys
import logging
import os
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))

if WARNING_THRESHOLD <= CRITICAL_THRESHOLD:
    logging.error("WARNING debe ser mayor que CRITICAL")
    sys.exit(2)
    
logging.info(
    f"Chequeando CPU "
    f"(warning={WARNING_THRESHOLD}% idle, "
    f"critical={CRITICAL_THRESHOLD}% idle)"
)

result = subprocess.run(
    ["top", "-bn1"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    logging.error("Fallo al ejecutar top")
    logging.error(result.stderr.strip())
    sys.exit(2)
    
cpu_line = None
for line in result.stdout.splitlines():
    if "Cpu(s)" in line:
        cpu_line=line
        break
    
if cpu_line is None:
    logging.error("No se encontró información de CPU")
    sys.exit(2)
    

match = re.search(r'(\d+\.?\d*)\s*id', cpu_line)

if not match:
    logging.error("No se pudo extraer el valor idle")
    logging.error(f"Línea parseada: {cpu_line}")
    sys.exit(2)
    
try:
    idle_percent = float(match.group(1))
except ValueError:
    logging.error("Error al convertir idle a número")
    sys.exit(2)
    
idle_percent = round(idle_percent, 1)

usage_percent = round(100 - idle_percent, 1)

if idle_percent >= WARNING_THRESHOLD:
    logging.info(
        f"OK - CPU idle: {idle_percent}% (uso: {usage_percent}%)"
    )
    sys.exit(0)
    
elif idle_percent >= CRITICAL_THRESHOLD:
    message=f"WARNING - CPU idle: {idle_percent}% (uso: {usage_percent}"
    logging.warning(message)
    
    send_alert(
        title= "Advertencia de CPU",
        message= message,
        level= "WARNING"
    )
    sys.exit(1)
    
else:
    message= f"CRITICAL - CPU idle: {idle_percent}% (uso: {usage_percent}%"
    logging.error(message)
    
    send_alert(
        title= "CRITICO uso de CPU",
        message= message,
        level= "CRITICAL"
    )
    sys.exit(2)
    

