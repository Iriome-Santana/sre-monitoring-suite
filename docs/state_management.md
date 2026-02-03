# State Management

Cada check guarda su último estado en un archivo:

/tmp/cpu.state
/tmp/memory.state
/tmp/disk.state

Esto permite:
- Detectar cambios de estado
- Evitar alertas repetidas
- Enviar alertas de recovery

Sin estado, cada ejecución generaría ruido.
