#!/bin/bash
# Log rotation profesional

LOG_DIR="$HOME/sre-monitoring-suite/logs"
RETENTION_DAYS=30
COMPRESS_DAYS=7

# Comprimir logs viejos (7+ días)
find "$LOG_DIR" -name "*.log" -type f -mtime +$COMPRESS_DAYS ! -name "*.gz" -exec gzip {} \;

# Borrar logs muy viejos (30+ días)
find "$LOG_DIR" -name "*.log.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "✅ Log rotation completado"
echo "   - Logs <7 días: sin comprimir"
echo "   - Logs 7-30 días: comprimidos (.gz)"
echo "   - Logs >30 días: eliminados"#!/bin/bash

find ~/sre/logs -name "*.log" -type f -mtime +5 -delete

echo "Logs antiguos eliminados (más de 5 días)"
