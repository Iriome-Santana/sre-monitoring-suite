#!/bin/bash

echo "=== Probando cpu_check.py ==="
echo ""

echo "1. Check normal (umbrales por defecto 20%/10% idle):"
python3 ~/sre/scripts/cpu_check.py
echo "Exit code: $?"
echo ""

echo "2. Check con umbrales altos (forzar warning):"
WARNING=80 CRITICAL=70 python3 ~/sre/scripts/cpu_check.py
echo "Exit code: $?"
echo ""
