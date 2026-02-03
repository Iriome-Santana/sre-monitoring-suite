# Lessons Learned

Durante el desarrollo de este proyecto
surgieron varios problemas reales que aportaron aprendizaje.

## 1. Variables de entorno no disponibles en cron

Problema:
El script funcionaba manualmente pero fallaba vía cron.

Causa:
Cron no carga el entorno del usuario.

Solución:
Definir variables explícitamente en el crontab
o cargarlas desde el script.

Aprendizaje:
Nunca asumir entorno en ejecución automatizada.

## 2. Alertas repetidas

Problema:
El sistema enviaba alertas en cada ejecución.

Causa:
No existía persistencia del estado previo.

Solución:
Implementar archivos de estado en /tmp.

Aprendizaje:
El alert fatigue es un problema real incluso
en sistemas pequeños.

## 3. Parsing frágil de comandos del sistema

Problema:
Cambios menores en la salida de comandos
rompían el parsing.

Solución:
Validar estructura y manejar errores explícitamente.

Aprendizaje:
Los sistemas reales fallan por casos no felices.
