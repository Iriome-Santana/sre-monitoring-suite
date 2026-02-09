# Verificación del Sistema

## Checklist Completo

### 1. Métricas Exporter
```bash
# Verificar que está corriendo
ps aux | grep metrics_exporter

# Verificar que expone métricas
curl http://localhost:8000/metrics | grep sre_
```

**Esperado:**
- Proceso de Python corriendo
- Tres métricas visibles: disk, memory, cpu

---

### 2. Prometheus
```bash
# Verificar contenedor
docker ps | grep prometheus

# Verificar health
curl http://localhost:9090/-/healthy
```

**Esperado:**
- Contenedor UP
- Respuesta: `Healthy`

**En navegador:**
- Abrir: http://localhost:9090/targets
- Estado: **UP** ✓

---

### 3. Grafana
```bash
# Verificar contenedor
docker ps | grep grafana

# Verificar health
curl http://localhost:3000/api/health
```

**Esperado:**
- Contenedor UP
- Respuesta JSON con `"database":"ok"`

**En navegador:**
- Abrir: http://localhost:3000
- Login funciona
- Dashboard visible y actualizándose

---

## Tests de Integración

### Test 1: Cambio en métricas se refleja en dashboard
```bash
# Crear archivo grande (aumenta uso de disco)
dd if=/dev/zero of=/tmp/test_file bs=1M count=500

# Observar:
# 1. curl http://localhost:8000/metrics | grep disk
#    → Valor debe haber subido
# 
# 2. Prometheus: http://localhost:9090
#    → Query: sre_disk_usage_percent
#    → Ver gráfico subiendo
#
# 3. Grafana dashboard
#    → Panel de disco debe mostrar aumento

# Limpiar
rm /tmp/test_file
```

### Test 2: Reinicio mantiene configuración
```bash
# Detener todo
docker-compose down

# Reiniciar
docker-compose up -d

# Verificar:
# - Grafana mantiene data source configurado
# - Dashboard existe
# - Métricas vuelven a aparecer
```

---

## Troubleshooting Común

### "No data" en Grafana

1. Verificar exporter: `curl http://localhost:8000/metrics`
2. Verificar Prometheus targets: http://localhost:9090/targets
3. Verificar data source en Grafana: debe ser `http://prometheus:9090`

### Exporter no inicia
```bash
# Ver logs
tail -f ~/sre-monitoring-suite/logs/metrics_exporter.log

# Verificar puerto libre
lsof -i :8000
```

### Prometheus no scrapea
```bash
# Ver logs
docker-compose logs prometheus | tail -20

# Verificar configuración
cat docker/prometheus/prometheus.yml
```
