# Troubleshooting

## No se envían alertas
- Verificar DISCORD_WEBHOOK
- Verificar NOTIFICATIONS_ENABLED
- Probar ejecución manual

## Alertas repetidas
- Verificar permisos de /tmp
- Verificar escritura del archivo .state

## Diferencias entre ejecución manual y cron
- Cron no carga variables de entorno
- Solución: definirlas en el script o en crontab
