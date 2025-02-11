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

gcloud sql instances create movie-db-prod \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=3rVIB8sVQfX2aYaZa57a

### 5. Configuración de Cloud SQL (PostgreSQL)

#### Crear la base de datos

gcloud sql databases create moviedb --instance=movie-db-prod

#### Crear usuario para la aplicación

gcloud sql users create movie-user \
  --instance=movie-db-prod \
  --password=movieUser2025Secure

```shell
eduardo@erl-portatil:~/Proyectos/brite$ gcloud sql instances create movie-db-prod \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=3rVIB8sVQfX2aYaZa57a
Creating Cloud SQL instance for POSTGRES_13...done.                                                 
Created [https://sqladmin.googleapis.com/sql/v1beta4/projects/brite-450618/instances/movie-db-prod].
NAME           DATABASE_VERSION  LOCATION       TIER         PRIMARY_ADDRESS  PRIVATE_ADDRESS  STATUS
movie-db-prod  POSTGRES_13       us-central1-a  db-f1-micro  34.55.52.78      -                RUNNABLE
eduardo@erl-portatil:~/Proyectos/brite$ gcloud sql databases create moviedb --instance=movie-db-prod
Creating Cloud SQL database...done.                                                                 
Created database [moviedb].
instance: movie-db-prod
name: moviedb
project: brite-450618
eduardo@erl-portatil:~/Proyectos/brite$ gcloud sql users create movie-user \
  --instance=movie-db-prod \
  --password=movieUser2025Secure
Creating Cloud SQL user...done.                                                                     
Created user [movie-user].

```

### 6. Configuración de Secret Manager

```shell
eduardo@erl-portatil:~/Proyectos/brite$ echo "postgresql+asyncpg://movie-user:movieUser2025Secure@/moviedb?host=/cloudsql/$(gcloud config get-value project):us-central1:movie-db-prod" | \
gcloud secrets create movie-db-url --data-file=-
Created version [1] of the secret [movie-db-url].
eduardo@erl-portatil:~/Proyectos/brite$ # Crear secreto para la API Key de OMDB
echo "tu_api_key_de_omdb" | \
gcloud secrets create omdb-api-key --data-file=-
Created version [1] of the secret [omdb-api-key].
eduardo@erl-portatil:~/Proyectos/brite$ export SERVICE_ACCOUNT="$(gcloud run services list --platform managed --format='value(serviceIdentity)')"
eduardo@erl-portatil:~/Proyectos/brite$ # Dar acceso a los secretos
gcloud secrets add-iam-policy-binding movie-db-url \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
ERROR: (gcloud.secrets.add-iam-policy-binding) Status code: 400. Invalid service account ()..
eduardo@erl-portatil:~/Proyectos/brite$ gcloud iam service-accounts create movie-backend-sa \
  --display-name="Movie Backend Service Account"
Created service account [movie-backend-sa].
eduardo@erl-portatil:~/Proyectos/brite$ export SERVICE_ACCOUNT="movie-backend-sa@$(gcloud config get-value project).iam.gserviceaccount.com"
eduardo@erl-portatil:~/Proyectos/brite$ gcloud secrets add-iam-policy-binding movie-db-url \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
Updated IAM policy for secret [movie-db-url].
bindings:
- members:
  - serviceAccount:movie-backend-sa@brite-450618.iam.gserviceaccount.com
  role: roles/secretmanager.secretAccessor
etag: BwYt4xtd9Qw=
version: 1
eduardo@erl-portatil:~/Proyectos/brite$ gcloud secrets add-iam-policy-binding omdb-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
Updated IAM policy for secret [omdb-api-key].
bindings:
- members:
  - serviceAccount:movie-backend-sa@brite-450618.iam.gserviceaccount.com
  role: roles/secretmanager.secretAccessor
etag: BwYt4x0up80=
version: 1
eduardo@erl-portatil:~/Proyectos/brite$ gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudsql.client"
Updated IAM policy for project [brite-450618].
bindings:
- members:
  - serviceAccount:58302029113@cloudbuild.gserviceaccount.com
  role: roles/cloudbuild.builds.builder
- members:
  - serviceAccount:service-58302029113@gcp-sa-cloudbuild.iam.gserviceaccount.com
  role: roles/cloudbuild.serviceAgent
- members:
  - serviceAccount:movie-backend-sa@brite-450618.iam.gserviceaccount.com
  role: roles/cloudsql.client
- members:
  - serviceAccount:service-58302029113@containerregistry.iam.gserviceaccount.com
  role: roles/containerregistry.ServiceAgent
- members:
  - serviceAccount:58302029113-compute@developer.gserviceaccount.com
  role: roles/editor
- members:
  - user:IngTecEduardo@gmail.com
  role: roles/owner
- members:
  - serviceAccount:service-58302029113@gcp-sa-pubsub.iam.gserviceaccount.com
  role: roles/pubsub.serviceAgent
- members:
  - serviceAccount:service-58302029113@serverless-robot-prod.iam.gserviceaccount.com
  role: roles/run.serviceAgent
etag: BwYt4x80Gao=
version: 1
```


## Próximos Pasos Pendientes

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