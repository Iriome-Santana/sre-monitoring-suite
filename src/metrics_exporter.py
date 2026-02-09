#!/usr/bin/env python3

"""
Exportador de métricas para Prometheus.
Expone métricas de sistema vía HTTP para que Prometheus las scrapee.

Este script corre de manera INDEPENDIENTE a los checks de cron.
Mientras disk_check.py maneja alertas, este expone métricas para grafana.
"""

from prometheus_client import start_http_server, Gauge
import subprocess
import time
import logging
import re
import os

METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))
SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "15"))

DISK_PATH = os.environ.get("DISK_PATH", "/")
LOG_DIR = os.path.expanduser("~/sre-monitoring-suite/logs")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/metrics_exporter.log"),
        logging.StreamHandler()
    ])

def collect_disk_usage():
    """Recoge el uso de disco usando df."""
    
    try:
        result = subprocess.run(
            ["df", "-h", DISK_PATH],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    use_percent_str = parts[4]
                    use_percent = int(use_percent_str.strip('%'))
                    return use_percent
        
        logging.error("Error parseando salida de df")
        return -1
    
    except Exception as e:
        logging.error(f"Error en collect_disk_usage: {e}")
        return -1
    
def collect_cpu_idle():
    """Recoge el porcentaje de CPU idle usando top."""
    
    try:
        result = subprocess.run(
            ["top", "-bn1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "Cpu(s)" in line:
                    match = re.search(r'(\d+\.?\d*)\s*id', line)
                    if match:
                        idle_percent = round(float(match.group(1)), 1)
                        return idle_percent
        
        logging.error("Error parseando salida de top")
        return -1
    
    except Exception as e:
        logging.error(f"Error en collect_cpu_idle: {e}")
        return -1
    
def collect_memory_available():
    """Recoge el porcentaje de memoria disponible usando free."""
    
    try:
        result = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            if len(lines) >= 2:
                mem_line = lines[1].split()
                if len(mem_line) >= 7:
                    total_mb = int(mem_line[1])
                    available_mb = int(mem_line[6])
                    available_percent = round((available_mb / total_mb) * 100, 1)
                    return available_percent
        
        logging.error("Error parseando salida de free")
        return -1
    
    except Exception as e:
        logging.error(f"Error en collect_memory_available: {e}")
        return -1
    
logging.info(f"Creando métricas de Prometheus")

disk_usage_metric = Gauge("sre_disk_usage_percent",
                          "Porcentaje de uso del disco")

cpu_idle_metric = Gauge("sre_cpu_idle_percent",
                        "Porcentaje de CPU idle")

memory_available_metric = Gauge("sre_memory_available_percent",
                                "Porcentaje de memoria disponible")

logging.info("Métricas creadas")

logging.info(f"Iniciando servidor HTTP en puerto {METRICS_PORT}")

try:
    start_http_server(METRICS_PORT)
    logging.info(f"Servidor HTTP iniciado en http://localhost:{METRICS_PORT}/metrics")
except Exception as e:
    logging.error(f"Error iniciando servidor HTTP: {e}")
    exit(1)
    
logging.info(f"Iniciando recolección cada {SCRAPE_INTERVAL} segundos...")
logging.info("Ctrl+C para detener")

try:
    while True:
        disk = collect_disk_usage()
        memory = collect_memory_available()
        cpu = collect_cpu_idle()
        
        if disk >= 0:
            disk_usage_metric.set(disk)
            logging.info(f"Disk usage: {disk}%")
        
        if memory >= 0:
            memory_available_metric.set(memory)
            logging.info(f"Memory available: {memory}%")
        
        if cpu >= 0:
            cpu_idle_metric.set(cpu)
            logging.info(f"CPU idle: {cpu}%")
            
        if int(time.time()) % (SCRAPE_INTERVAL * 5) == 0:
            logging.info(f"Métricas actualizadas - Disco: {disk}%, Memoria: {memory}%, CPU: {cpu}%")
            
        time.sleep(SCRAPE_INTERVAL)

except KeyboardInterrupt:
    logging.info("Deteniendo exporter por interrupción del usuario")
except Exception as e:
    logging.error(f"Error en el loop principal: {e}")
    exit(1)
        
        
