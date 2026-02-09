# Configuración de Grafana

## Importar Dashboard

1. Abrir Grafana: http://localhost:3000
2. Login: `admin` / `admin`
3. Click **☰** → **Dashboards** → **New** → **Import**
4. Click **"Upload JSON file"**
5. Seleccionar `docs/dashboard.json`
6. En "Prometheus" dropdown, seleccionar data source
7. Click **"Import"**

## Data Source

Si necesitas configurar el data source manualmente:

1. **☰** → **Connections** → **Data sources**
2. Click **"Add data source"**
3. Seleccionar **"Prometheus"**
4. Configurar:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090` (si usas Docker Compose) o `http://localhost:9090`
5. Click **"Save & test"**

## Métricas Disponibles

- `sre_disk_usage_percent`: Uso de disco en porcentaje
- `sre_memory_available_percent`: Memoria disponible en porcentaje
- `sre_cpu_idle_percent`: CPU idle en porcentaje
```
