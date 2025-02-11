# Guía de Despliegue del Backend en Google Cloud Run

## Prerrequisitos

1. Tener instalado Google Cloud SDK
2. Tener una cuenta de Google Cloud Platform con facturación habilitada
3. Tener el proyecto creado en Google Cloud
4. Tener Docker instalado localmente

## 1. Configuración Inicial de Google Cloud

```bash
# Iniciar sesión en Google Cloud
gcloud auth login

# Configurar el proyecto
gcloud config set project [your-project-id]

# Habilitar las APIs necesarias
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com
```

## 2. Configuración de Cloud SQL

1. Crear una instancia de PostgreSQL:
```bash
gcloud sql instances create movie-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=[your-password]
```

2. Crear la base de datos:
```bash
gcloud sql databases create moviedb --instance=movie-db
```

3. Crear usuario de la base de datos:
```bash
gcloud sql users create movie-user \
  --instance=movie-db \
  --password=[your-password]
```

## 3. Configuración de Secret Manager

1. Crear los secretos necesarios:
```bash
# URL de la base de datos
echo "postgresql+asyncpg://movie-user:[password]@/moviedb?host=/cloudsql/[project-id]:us-central1:movie-db" | \
gcloud secrets create movie-db-url --data-file=-

# API Key de OMDB
echo "[your-omdb-api-key]" | \
gcloud secrets create omdb-api-key --data-file=-
```

2. Dar acceso a Cloud Run para leer los secretos:
```bash
# Obtener el Service Account de Cloud Run
export SERVICE_ACCOUNT="$(gcloud run services list --platform managed --format='value(serviceIdentity)')"

# Dar acceso a los secretos
gcloud secrets add-iam-policy-binding movie-db-url \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding omdb-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

## 4. Preparación del Dockerfile

Asegúrate de que tu Dockerfile en `backend/app/Dockerfile` esté correctamente configurado:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv para mejor manejo de dependencias
RUN pip install uv

# Copiar requirements primero para aprovechar la caché
COPY ../requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Variable de entorno para el puerto (requerida por Cloud Run)
ENV PORT=8000

# Comando para ejecutar la aplicación
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

## 5. Configuración de Variables de Entorno

Crear un archivo `backend/.env.yaml` para Cloud Run:

```yaml
DATABASE_URL: "postgresql+asyncpg://movie-user:[password]@/moviedb?host=/cloudsql/[project-id]:us-central1:movie-db"
GOOGLE_CLOUD_PROJECT: "[project-id]"
OMDB_API_KEY: "[your-omdb-api-key]"
```

## 6. Despliegue en Cloud Run

1. Construir y subir la imagen a Container Registry:
```bash
# Desde el directorio backend
gcloud builds submit --tag gcr.io/[project-id]/movie-backend
```

2. Desplegar el servicio en Cloud Run:
```bash
gcloud run deploy movie-backend \
  --image gcr.io/[project-id]/movie-backend \
  --platform managed \
  --region us-central1 \
  --env-vars-file .env.yaml \
  --add-cloudsql-instances [project-id]:us-central1:movie-db \
  --allow-unauthenticated
```

## 7. Verificación del Despliegue

1. Obtener la URL del servicio:
```bash
gcloud run services describe movie-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

2. Verificar el estado del servicio:
```bash
curl [service-url]/health
```

## 8. Monitoreo y Logs

1. Ver logs en tiempo real:
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=movie-backend"
```

2. Configurar alertas de errores:
```bash
gcloud beta monitoring alerting policies create \
  --display-name="Movie Backend Errors" \
  --condition="metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" metric.label.\"response_code\">=\"500\"" \
  --notification-channels="[your-notification-channel]" \
  --threshold-value=5 \
  --threshold-time=300s
```

## Notas Importantes

- Asegúrate de reemplazar todos los valores entre `[]` con tus valores específicos
- Mantén seguros tus secretos y no los compartas en el control de versiones
- Considera usar CI/CD para automatizar los despliegues
- Revisa regularmente los logs y métricas para monitorear el rendimiento
- Configura copias de seguridad automáticas de la base de datos

## Troubleshooting Común

1. Error de conexión a la base de datos:
   - Verifica que la instancia de Cloud SQL esté activa
   - Confirma que el usuario y contraseña sean correctos
   - Revisa la configuración del Cloud SQL Auth Proxy

2. Error en las variables de entorno:
   - Verifica que el archivo .env.yaml esté correctamente formateado
   - Confirma que todas las variables requeridas estén definidas

3. Errores de memoria:
   - Ajusta los límites de recursos en Cloud Run
   - Optimiza las consultas a la base de datos
   - Considera usar caching