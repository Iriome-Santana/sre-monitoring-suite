#!/bin/bash

# Cargar configuración
source ~/sre/config.env

# Generar reporte
REPORT=$(~/sre/scripts/daily_report.sh)

# Enviar a Discord usando Python
python3 - <<EOF
from notifier import send_alert
import sys
import os

# Configurar webhook
os.environ["DISCORD_WEBHOOK"] = "$DISCORD_WEBHOOK"

# Enviar resumen
send_alert(
    title="📊 Resumen Diario de Monitoreo",
    message="""$REPORT""",
    level="INFO"
)
EOF

echo "Resumen enviado a Discord"
