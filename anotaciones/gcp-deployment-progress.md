# Registro de Despliegue en Google Cloud Platform

## Fecha: 11/02/2025

### 1. Instalación de Google Cloud SDK

```bash
# Instalación usando snap (Ubuntu 22.04)
sudo snap install google-cloud-sdk --classic
```

### 2. Inicialización y Configuración

```bash
# Inicializar Google Cloud SDK
gcloud init
```

### 3. Habilitación de APIs Necesarias

```bash
# Habilitar las APIs requeridas
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com
```
### 4. Configuración de Cloud SQL (PostgreSQL)

gcloud sql instances create movie-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=3rVIB8sVQfX2|YaZa57a



## Próximos Pasos Pendientes

- [ ] Configuración de Cloud SQL (PostgreSQL)
- [ ] Configuración de Secret Manager
- [ ] Preparación del Dockerfile
- [ ] Configuración de variables de entorno
- [ ] Despliegue en Cloud Run
- [ ] Verificación del despliegue
- [ ] Configuración de monitoreo y logs

## Notas Importantes
- Se ha habilitado la facturación en el proyecto
- Las APIs necesarias están habilitadas y funcionando correctamente

## Errores Encontrados y Soluciones
1. Error inicial de facturación:
   - Problema: FAILED_PRECONDITION al habilitar servicios
   - Solución: Se habilitó la facturación en la consola de GCP