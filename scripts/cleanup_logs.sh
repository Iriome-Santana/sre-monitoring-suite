#!/bin/bash

find ~/sre/logs -name "*.log" -type f -mtime +5 -delete

echo "Logs antiguos eliminados (más de 5 días)"
