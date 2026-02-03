# Technical Decisions

## Why idle CPU instead of load average?
El idle time refleja directamente la capacidad disponible
y es fácil de interpretar para alerting.

## Why variables de entorno?
Permiten modificar comportamiento sin cambiar código,
siguiendo principios 12-factor.

## Why state files en /tmp?
Simplicidad y persistencia entre ejecuciones
sin necesidad de base de datos.

## Why Discord?
Rápido, visual y suficiente para entornos pequeños.
