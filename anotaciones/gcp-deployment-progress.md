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

los tres puntos siguentes hacen referencia al codigo mostrado a continuación.

#### Preparación del Dockerfile
#### Configuración de variables de entorno
#### Despliegue en Cloud Run


```shell
eduardo@erl-portatil:~/Proyectos/brite/movie-app/backend$ gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/movie-backend
Creating temporary archive of 1299 file(s) totalling 274.3 MiB before compression.
Uploading tarball of [.] to [gs://brite-450618_cloudbuild/source/1739307201.750908-534e0ae3df7947ca947b84acd0d7c05a.tgz]
Created [https://cloudbuild.googleapis.com/v1/projects/brite-450618/locations/global/builds/0fdc98cd-200a-4312-a6ab-829049eb1975].
Logs are available at [ https://console.cloud.google.com/cloud-build/builds/0fdc98cd-200a-4312-a6ab-829049eb1975?project=58302029113 ].
Waiting for build to complete. Polling interval: 1 second(s).
------------------------------------------------------------------------------------------- REMOTE BUILD OUTPUT --------------------------------------------------------------------------------------------
starting build "0fdc98cd-200a-4312-a6ab-829049eb1975"

FETCHSOURCE
Fetching storage object: gs://brite-450618_cloudbuild/source/1739307201.750908-534e0ae3df7947ca947b84acd0d7c05a.tgz#1739307229163817
Copying gs://brite-450618_cloudbuild/source/1739307201.750908-534e0ae3df7947ca947b84acd0d7c05a.tgz#1739307229163817...
/ [1 files][ 19.7 MiB/ 19.7 MiB]                                                
Operation completed over 1 objects/19.7 MiB.
BUILD
Already have image (with digest): gcr.io/cloud-builders/docker
Sending build context to Docker daemon  193.6MB
Step 1/9 : FROM python:3.11-slim
3.11-slim: Pulling from library/python
c29f5b76f736: Already exists
73c4bbda278d: Pulling fs layer
acc53c3e87ac: Pulling fs layer
ad3b14759e4f: Pulling fs layer
ad3b14759e4f: Verifying Checksum
ad3b14759e4f: Download complete
73c4bbda278d: Verifying Checksum
73c4bbda278d: Download complete
acc53c3e87ac: Download complete
73c4bbda278d: Pull complete
acc53c3e87ac: Pull complete
ad3b14759e4f: Pull complete
Digest: sha256:42420f737ba91d509fc60d5ed65ed0492678a90c561e1fa08786ae8ba8b52eda
Status: Downloaded newer image for python:3.11-slim
 ---> 2c2c44fb54ac
Step 2/9 : WORKDIR /app
 ---> Running in 3dc066a280c0
Removing intermediate container 3dc066a280c0
 ---> ee19a1cc5aa4
Step 3/9 : RUN apt-get update && apt-get install -y     gcc     && rm -rf /var/lib/apt/lists/*
 ---> Running in 23346448fa1c
Get:1 http://deb.debian.org/debian bookworm InRelease [151 kB]
Get:2 http://deb.debian.org/debian bookworm-updates InRelease [55.4 kB]
Get:3 http://deb.debian.org/debian-security bookworm-security InRelease [48.0 kB]
Get:4 http://deb.debian.org/debian bookworm/main amd64 Packages [8792 kB]
Get:5 http://deb.debian.org/debian bookworm-updates/main amd64 Packages [13.5 kB]
Get:6 http://deb.debian.org/debian-security bookworm-security/main amd64 Packages [245 kB]
Fetched 9305 kB in 2s (5547 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cpp cpp-12
  fontconfig-config fonts-dejavu-core gcc-12 libabsl20220623 libaom3 libasan8
  libatomic1 libavif15 libbinutils libbrotli1 libbsd0 libc-dev-bin
  libc-devtools libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0
  libdav1d6 libde265-0 libdeflate0 libexpat1 libfontconfig1 libfreetype6
  libgav1-1 libgcc-12-dev libgd3 libgomp1 libgprofng0 libheif1 libisl23
  libitm1 libjansson4 libjbig0 libjpeg62-turbo liblerc4 liblsan0 libmpc3
  libmpfr6 libnsl-dev libnuma1 libpng16-16 libquadmath0 librav1e0
  libsvtav1enc1 libtiff6 libtirpc-dev libtsan2 libubsan1 libwebp7 libx11-6
  libx11-data libx265-199 libxau6 libxcb1 libxdmcp6 libxpm4 libyuv0
  linux-libc-dev manpages manpages-dev rpcsvc-proto
Suggested packages:
  binutils-doc cpp-doc gcc-12-locales cpp-12-doc gcc-multilib make autoconf
  automake libtool flex bison gdb gcc-doc gcc-12-multilib gcc-12-doc glibc-doc
  libgd-tools man-browser
The following NEW packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cpp cpp-12
  fontconfig-config fonts-dejavu-core gcc gcc-12 libabsl20220623 libaom3
  libasan8 libatomic1 libavif15 libbinutils libbrotli1 libbsd0 libc-dev-bin
  libc-devtools libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0
  libdav1d6 libde265-0 libdeflate0 libexpat1 libfontconfig1 libfreetype6
  libgav1-1 libgcc-12-dev libgd3 libgomp1 libgprofng0 libheif1 libisl23
  libitm1 libjansson4 libjbig0 libjpeg62-turbo liblerc4 liblsan0 libmpc3
  libmpfr6 libnsl-dev libnuma1 libpng16-16 libquadmath0 librav1e0
  libsvtav1enc1 libtiff6 libtirpc-dev libtsan2 libubsan1 libwebp7 libx11-6
  libx11-data libx265-199 libxau6 libxcb1 libxdmcp6 libxpm4 libyuv0
  linux-libc-dev manpages manpages-dev rpcsvc-proto
0 upgraded, 68 newly installed, 0 to remove and 1 not upgraded.
Need to get 67.1 MB of archives.
After this operation, 259 MB of additional disk space will be used.
Get:1 http://deb.debian.org/debian bookworm/main amd64 manpages all 6.03-2 [1332 kB]
Get:2 http://deb.debian.org/debian bookworm/main amd64 binutils-common amd64 2.40-2 [2487 kB]
Get:3 http://deb.debian.org/debian bookworm/main amd64 libbinutils amd64 2.40-2 [572 kB]
Get:4 http://deb.debian.org/debian bookworm/main amd64 libctf-nobfd0 amd64 2.40-2 [153 kB]
Get:5 http://deb.debian.org/debian bookworm/main amd64 libctf0 amd64 2.40-2 [89.8 kB]
Get:6 http://deb.debian.org/debian bookworm/main amd64 libgprofng0 amd64 2.40-2 [812 kB]
Get:7 http://deb.debian.org/debian bookworm/main amd64 libjansson4 amd64 2.14-2 [40.8 kB]
Get:8 http://deb.debian.org/debian bookworm/main amd64 binutils-x86-64-linux-gnu amd64 2.40-2 [2246 kB]
Get:9 http://deb.debian.org/debian bookworm/main amd64 binutils amd64 2.40-2 [65.0 kB]
Get:10 http://deb.debian.org/debian bookworm/main amd64 libisl23 amd64 0.25-1.1 [683 kB]
Get:11 http://deb.debian.org/debian bookworm/main amd64 libmpfr6 amd64 4.2.0-1 [701 kB]
Get:12 http://deb.debian.org/debian bookworm/main amd64 libmpc3 amd64 1.3.1-1 [51.5 kB]
Get:13 http://deb.debian.org/debian bookworm/main amd64 cpp-12 amd64 12.2.0-14 [9764 kB]
Get:14 http://deb.debian.org/debian bookworm/main amd64 cpp amd64 4:12.2.0-3 [6836 B]
Get:15 http://deb.debian.org/debian bookworm/main amd64 fonts-dejavu-core all 2.37-6 [1068 kB]
Get:16 http://deb.debian.org/debian bookworm/main amd64 fontconfig-config amd64 2.14.1-4 [315 kB]
Get:17 http://deb.debian.org/debian bookworm/main amd64 libcc1-0 amd64 12.2.0-14 [41.7 kB]
Get:18 http://deb.debian.org/debian bookworm/main amd64 libgomp1 amd64 12.2.0-14 [116 kB]
Get:19 http://deb.debian.org/debian bookworm/main amd64 libitm1 amd64 12.2.0-14 [26.1 kB]
Get:20 http://deb.debian.org/debian bookworm/main amd64 libatomic1 amd64 12.2.0-14 [9328 B]
Get:21 http://deb.debian.org/debian bookworm/main amd64 libasan8 amd64 12.2.0-14 [2195 kB]
Get:22 http://deb.debian.org/debian bookworm/main amd64 liblsan0 amd64 12.2.0-14 [969 kB]
Get:23 http://deb.debian.org/debian bookworm/main amd64 libtsan2 amd64 12.2.0-14 [2196 kB]
Get:24 http://deb.debian.org/debian bookworm/main amd64 libubsan1 amd64 12.2.0-14 [883 kB]
Get:25 http://deb.debian.org/debian bookworm/main amd64 libquadmath0 amd64 12.2.0-14 [144 kB]
Get:26 http://deb.debian.org/debian bookworm/main amd64 libgcc-12-dev amd64 12.2.0-14 [2437 kB]
Get:27 http://deb.debian.org/debian bookworm/main amd64 gcc-12 amd64 12.2.0-14 [19.3 MB]
Get:28 http://deb.debian.org/debian bookworm/main amd64 gcc amd64 4:12.2.0-3 [5216 B]
Get:29 http://deb.debian.org/debian bookworm/main amd64 libabsl20220623 amd64 20220623.1-1 [391 kB]
Get:30 http://deb.debian.org/debian bookworm/main amd64 libaom3 amd64 3.6.0-1+deb12u1 [1851 kB]
Get:31 http://deb.debian.org/debian bookworm/main amd64 libdav1d6 amd64 1.0.0-2+deb12u1 [513 kB]
Get:32 http://deb.debian.org/debian bookworm/main amd64 libgav1-1 amd64 0.18.0-1+b1 [332 kB]
Get:33 http://deb.debian.org/debian bookworm/main amd64 librav1e0 amd64 0.5.1-6 [763 kB]
Get:34 http://deb.debian.org/debian bookworm/main amd64 libsvtav1enc1 amd64 1.4.1+dfsg-1 [2121 kB]
Get:35 http://deb.debian.org/debian bookworm/main amd64 libjpeg62-turbo amd64 1:2.1.5-2 [166 kB]
Get:36 http://deb.debian.org/debian bookworm/main amd64 libyuv0 amd64 0.0~git20230123.b2528b0-1 [168 kB]
Get:37 http://deb.debian.org/debian bookworm/main amd64 libavif15 amd64 0.11.1-1 [93.8 kB]
Get:38 http://deb.debian.org/debian bookworm/main amd64 libbrotli1 amd64 1.0.9-2+b6 [275 kB]
Get:39 http://deb.debian.org/debian bookworm/main amd64 libbsd0 amd64 0.11.7-2 [117 kB]
Get:40 http://deb.debian.org/debian bookworm/main amd64 libc-dev-bin amd64 2.36-9+deb12u9 [46.7 kB]
Get:41 http://deb.debian.org/debian bookworm/main amd64 libexpat1 amd64 2.5.0-1+deb12u1 [98.9 kB]
Get:42 http://deb.debian.org/debian bookworm/main amd64 libpng16-16 amd64 1.6.39-2 [276 kB]
Get:43 http://deb.debian.org/debian bookworm/main amd64 libfreetype6 amd64 2.12.1+dfsg-5+deb12u3 [398 kB]
Get:44 http://deb.debian.org/debian bookworm/main amd64 libfontconfig1 amd64 2.14.1-4 [386 kB]
Get:45 http://deb.debian.org/debian bookworm/main amd64 libde265-0 amd64 1.0.11-1+deb12u2 [185 kB]
Get:46 http://deb.debian.org/debian bookworm/main amd64 libnuma1 amd64 2.0.16-1 [21.0 kB]
Get:47 http://deb.debian.org/debian bookworm/main amd64 libx265-199 amd64 3.5-2+b1 [1150 kB]
Get:48 http://deb.debian.org/debian bookworm/main amd64 libheif1 amd64 1.15.1-1+deb12u1 [215 kB]
Get:49 http://deb.debian.org/debian bookworm/main amd64 libdeflate0 amd64 1.14-1 [61.4 kB]
Get:50 http://deb.debian.org/debian bookworm/main amd64 libjbig0 amd64 2.1-6.1 [31.7 kB]
Get:51 http://deb.debian.org/debian bookworm/main amd64 liblerc4 amd64 4.0.0+ds-2 [170 kB]
Get:52 http://deb.debian.org/debian bookworm/main amd64 libwebp7 amd64 1.2.4-0.2+deb12u1 [286 kB]
Get:53 http://deb.debian.org/debian bookworm/main amd64 libtiff6 amd64 4.5.0-6+deb12u2 [316 kB]
Get:54 http://deb.debian.org/debian bookworm/main amd64 libxau6 amd64 1:1.0.9-1 [19.7 kB]
Get:55 http://deb.debian.org/debian bookworm/main amd64 libxdmcp6 amd64 1:1.1.2-3 [26.3 kB]
Get:56 http://deb.debian.org/debian bookworm/main amd64 libxcb1 amd64 1.15-1 [144 kB]
Get:57 http://deb.debian.org/debian bookworm/main amd64 libx11-data all 2:1.8.4-2+deb12u2 [292 kB]
Get:58 http://deb.debian.org/debian bookworm/main amd64 libx11-6 amd64 2:1.8.4-2+deb12u2 [760 kB]
Get:59 http://deb.debian.org/debian bookworm/main amd64 libxpm4 amd64 1:3.5.12-1.1+deb12u1 [48.6 kB]
Get:60 http://deb.debian.org/debian bookworm/main amd64 libgd3 amd64 2.3.3-9 [124 kB]
Get:61 http://deb.debian.org/debian bookworm/main amd64 libc-devtools amd64 2.36-9+deb12u9 [54.4 kB]
Get:62 http://deb.debian.org/debian-security bookworm-security/main amd64 linux-libc-dev amd64 6.1.128-1 [2103 kB]
Get:63 http://deb.debian.org/debian bookworm/main amd64 libcrypt-dev amd64 1:4.4.33-2 [118 kB]
Get:64 http://deb.debian.org/debian bookworm/main amd64 libtirpc-dev amd64 1.3.3+ds-1 [191 kB]
Get:65 http://deb.debian.org/debian bookworm/main amd64 libnsl-dev amd64 1.3.0-2 [66.4 kB]
Get:66 http://deb.debian.org/debian bookworm/main amd64 rpcsvc-proto amd64 1.4.3-1 [63.3 kB]
Get:67 http://deb.debian.org/debian bookworm/main amd64 libc6-dev amd64 2.36-9+deb12u9 [1904 kB]
Get:68 http://deb.debian.org/debian bookworm/main amd64 manpages-dev all 6.03-2 [2030 kB]
debconf: delaying package configuration, since apt-utils is not installed
Fetched 67.1 MB in 1s (101 MB/s)
Selecting previously unselected package manpages.
(Reading database ... 6686 files and directories currently installed.)
Preparing to unpack .../00-manpages_6.03-2_all.deb ...
Unpacking manpages (6.03-2) ...
Selecting previously unselected package binutils-common:amd64.
Preparing to unpack .../01-binutils-common_2.40-2_amd64.deb ...
Unpacking binutils-common:amd64 (2.40-2) ...
Selecting previously unselected package libbinutils:amd64.
Preparing to unpack .../02-libbinutils_2.40-2_amd64.deb ...
Unpacking libbinutils:amd64 (2.40-2) ...
Selecting previously unselected package libctf-nobfd0:amd64.
Preparing to unpack .../03-libctf-nobfd0_2.40-2_amd64.deb ...
Unpacking libctf-nobfd0:amd64 (2.40-2) ...
Selecting previously unselected package libctf0:amd64.
Preparing to unpack .../04-libctf0_2.40-2_amd64.deb ...
Unpacking libctf0:amd64 (2.40-2) ...
Selecting previously unselected package libgprofng0:amd64.
Preparing to unpack .../05-libgprofng0_2.40-2_amd64.deb ...
Unpacking libgprofng0:amd64 (2.40-2) ...
Selecting previously unselected package libjansson4:amd64.
Preparing to unpack .../06-libjansson4_2.14-2_amd64.deb ...
Unpacking libjansson4:amd64 (2.14-2) ...
Selecting previously unselected package binutils-x86-64-linux-gnu.
Preparing to unpack .../07-binutils-x86-64-linux-gnu_2.40-2_amd64.deb ...
Unpacking binutils-x86-64-linux-gnu (2.40-2) ...
Selecting previously unselected package binutils.
Preparing to unpack .../08-binutils_2.40-2_amd64.deb ...
Unpacking binutils (2.40-2) ...
Selecting previously unselected package libisl23:amd64.
Preparing to unpack .../09-libisl23_0.25-1.1_amd64.deb ...
Unpacking libisl23:amd64 (0.25-1.1) ...
Selecting previously unselected package libmpfr6:amd64.
Preparing to unpack .../10-libmpfr6_4.2.0-1_amd64.deb ...
Unpacking libmpfr6:amd64 (4.2.0-1) ...
Selecting previously unselected package libmpc3:amd64.
Preparing to unpack .../11-libmpc3_1.3.1-1_amd64.deb ...
Unpacking libmpc3:amd64 (1.3.1-1) ...
Selecting previously unselected package cpp-12.
Preparing to unpack .../12-cpp-12_12.2.0-14_amd64.deb ...
Unpacking cpp-12 (12.2.0-14) ...
Selecting previously unselected package cpp.
Preparing to unpack .../13-cpp_4%3a12.2.0-3_amd64.deb ...
Unpacking cpp (4:12.2.0-3) ...
Selecting previously unselected package fonts-dejavu-core.
Preparing to unpack .../14-fonts-dejavu-core_2.37-6_all.deb ...
Unpacking fonts-dejavu-core (2.37-6) ...
Selecting previously unselected package fontconfig-config.
Preparing to unpack .../15-fontconfig-config_2.14.1-4_amd64.deb ...
Unpacking fontconfig-config (2.14.1-4) ...
Selecting previously unselected package libcc1-0:amd64.
Preparing to unpack .../16-libcc1-0_12.2.0-14_amd64.deb ...
Unpacking libcc1-0:amd64 (12.2.0-14) ...
Selecting previously unselected package libgomp1:amd64.
Preparing to unpack .../17-libgomp1_12.2.0-14_amd64.deb ...
Unpacking libgomp1:amd64 (12.2.0-14) ...
Selecting previously unselected package libitm1:amd64.
Preparing to unpack .../18-libitm1_12.2.0-14_amd64.deb ...
Unpacking libitm1:amd64 (12.2.0-14) ...
Selecting previously unselected package libatomic1:amd64.
Preparing to unpack .../19-libatomic1_12.2.0-14_amd64.deb ...
Unpacking libatomic1:amd64 (12.2.0-14) ...
Selecting previously unselected package libasan8:amd64.
Preparing to unpack .../20-libasan8_12.2.0-14_amd64.deb ...
Unpacking libasan8:amd64 (12.2.0-14) ...
Selecting previously unselected package liblsan0:amd64.
Preparing to unpack .../21-liblsan0_12.2.0-14_amd64.deb ...
Unpacking liblsan0:amd64 (12.2.0-14) ...
Selecting previously unselected package libtsan2:amd64.
Preparing to unpack .../22-libtsan2_12.2.0-14_amd64.deb ...
Unpacking libtsan2:amd64 (12.2.0-14) ...
Selecting previously unselected package libubsan1:amd64.
Preparing to unpack .../23-libubsan1_12.2.0-14_amd64.deb ...
Unpacking libubsan1:amd64 (12.2.0-14) ...
Selecting previously unselected package libquadmath0:amd64.
Preparing to unpack .../24-libquadmath0_12.2.0-14_amd64.deb ...
Unpacking libquadmath0:amd64 (12.2.0-14) ...
Selecting previously unselected package libgcc-12-dev:amd64.
Preparing to unpack .../25-libgcc-12-dev_12.2.0-14_amd64.deb ...
Unpacking libgcc-12-dev:amd64 (12.2.0-14) ...
Selecting previously unselected package gcc-12.
Preparing to unpack .../26-gcc-12_12.2.0-14_amd64.deb ...
Unpacking gcc-12 (12.2.0-14) ...
Selecting previously unselected package gcc.
Preparing to unpack .../27-gcc_4%3a12.2.0-3_amd64.deb ...
Unpacking gcc (4:12.2.0-3) ...
Selecting previously unselected package libabsl20220623:amd64.
Preparing to unpack .../28-libabsl20220623_20220623.1-1_amd64.deb ...
Unpacking libabsl20220623:amd64 (20220623.1-1) ...
Selecting previously unselected package libaom3:amd64.
Preparing to unpack .../29-libaom3_3.6.0-1+deb12u1_amd64.deb ...
Unpacking libaom3:amd64 (3.6.0-1+deb12u1) ...
Selecting previously unselected package libdav1d6:amd64.
Preparing to unpack .../30-libdav1d6_1.0.0-2+deb12u1_amd64.deb ...
Unpacking libdav1d6:amd64 (1.0.0-2+deb12u1) ...
Selecting previously unselected package libgav1-1:amd64.
Preparing to unpack .../31-libgav1-1_0.18.0-1+b1_amd64.deb ...
Unpacking libgav1-1:amd64 (0.18.0-1+b1) ...
Selecting previously unselected package librav1e0:amd64.
Preparing to unpack .../32-librav1e0_0.5.1-6_amd64.deb ...
Unpacking librav1e0:amd64 (0.5.1-6) ...
Selecting previously unselected package libsvtav1enc1:amd64.
Preparing to unpack .../33-libsvtav1enc1_1.4.1+dfsg-1_amd64.deb ...
Unpacking libsvtav1enc1:amd64 (1.4.1+dfsg-1) ...
Selecting previously unselected package libjpeg62-turbo:amd64.
Preparing to unpack .../34-libjpeg62-turbo_1%3a2.1.5-2_amd64.deb ...
Unpacking libjpeg62-turbo:amd64 (1:2.1.5-2) ...
Selecting previously unselected package libyuv0:amd64.
Preparing to unpack .../35-libyuv0_0.0~git20230123.b2528b0-1_amd64.deb ...
Unpacking libyuv0:amd64 (0.0~git20230123.b2528b0-1) ...
Selecting previously unselected package libavif15:amd64.
Preparing to unpack .../36-libavif15_0.11.1-1_amd64.deb ...
Unpacking libavif15:amd64 (0.11.1-1) ...
Selecting previously unselected package libbrotli1:amd64.
Preparing to unpack .../37-libbrotli1_1.0.9-2+b6_amd64.deb ...
Unpacking libbrotli1:amd64 (1.0.9-2+b6) ...
Selecting previously unselected package libbsd0:amd64.
Preparing to unpack .../38-libbsd0_0.11.7-2_amd64.deb ...
Unpacking libbsd0:amd64 (0.11.7-2) ...
Selecting previously unselected package libc-dev-bin.
Preparing to unpack .../39-libc-dev-bin_2.36-9+deb12u9_amd64.deb ...
Unpacking libc-dev-bin (2.36-9+deb12u9) ...
Selecting previously unselected package libexpat1:amd64.
Preparing to unpack .../40-libexpat1_2.5.0-1+deb12u1_amd64.deb ...
Unpacking libexpat1:amd64 (2.5.0-1+deb12u1) ...
Selecting previously unselected package libpng16-16:amd64.
Preparing to unpack .../41-libpng16-16_1.6.39-2_amd64.deb ...
Unpacking libpng16-16:amd64 (1.6.39-2) ...
Selecting previously unselected package libfreetype6:amd64.
Preparing to unpack .../42-libfreetype6_2.12.1+dfsg-5+deb12u3_amd64.deb ...
Unpacking libfreetype6:amd64 (2.12.1+dfsg-5+deb12u3) ...
Selecting previously unselected package libfontconfig1:amd64.
Preparing to unpack .../43-libfontconfig1_2.14.1-4_amd64.deb ...
Unpacking libfontconfig1:amd64 (2.14.1-4) ...
Selecting previously unselected package libde265-0:amd64.
Preparing to unpack .../44-libde265-0_1.0.11-1+deb12u2_amd64.deb ...
Unpacking libde265-0:amd64 (1.0.11-1+deb12u2) ...
Selecting previously unselected package libnuma1:amd64.
Preparing to unpack .../45-libnuma1_2.0.16-1_amd64.deb ...
Unpacking libnuma1:amd64 (2.0.16-1) ...
Selecting previously unselected package libx265-199:amd64.
Preparing to unpack .../46-libx265-199_3.5-2+b1_amd64.deb ...
Unpacking libx265-199:amd64 (3.5-2+b1) ...
Selecting previously unselected package libheif1:amd64.
Preparing to unpack .../47-libheif1_1.15.1-1+deb12u1_amd64.deb ...
Unpacking libheif1:amd64 (1.15.1-1+deb12u1) ...
Selecting previously unselected package libdeflate0:amd64.
Preparing to unpack .../48-libdeflate0_1.14-1_amd64.deb ...
Unpacking libdeflate0:amd64 (1.14-1) ...
Selecting previously unselected package libjbig0:amd64.
Preparing to unpack .../49-libjbig0_2.1-6.1_amd64.deb ...
Unpacking libjbig0:amd64 (2.1-6.1) ...
Selecting previously unselected package liblerc4:amd64.
Preparing to unpack .../50-liblerc4_4.0.0+ds-2_amd64.deb ...
Unpacking liblerc4:amd64 (4.0.0+ds-2) ...
Selecting previously unselected package libwebp7:amd64.
Preparing to unpack .../51-libwebp7_1.2.4-0.2+deb12u1_amd64.deb ...
Unpacking libwebp7:amd64 (1.2.4-0.2+deb12u1) ...
Selecting previously unselected package libtiff6:amd64.
Preparing to unpack .../52-libtiff6_4.5.0-6+deb12u2_amd64.deb ...
Unpacking libtiff6:amd64 (4.5.0-6+deb12u2) ...
Selecting previously unselected package libxau6:amd64.
Preparing to unpack .../53-libxau6_1%3a1.0.9-1_amd64.deb ...
Unpacking libxau6:amd64 (1:1.0.9-1) ...
Selecting previously unselected package libxdmcp6:amd64.
Preparing to unpack .../54-libxdmcp6_1%3a1.1.2-3_amd64.deb ...
Unpacking libxdmcp6:amd64 (1:1.1.2-3) ...
Selecting previously unselected package libxcb1:amd64.
Preparing to unpack .../55-libxcb1_1.15-1_amd64.deb ...
Unpacking libxcb1:amd64 (1.15-1) ...
Selecting previously unselected package libx11-data.
Preparing to unpack .../56-libx11-data_2%3a1.8.4-2+deb12u2_all.deb ...
Unpacking libx11-data (2:1.8.4-2+deb12u2) ...
Selecting previously unselected package libx11-6:amd64.
Preparing to unpack .../57-libx11-6_2%3a1.8.4-2+deb12u2_amd64.deb ...
Unpacking libx11-6:amd64 (2:1.8.4-2+deb12u2) ...
Selecting previously unselected package libxpm4:amd64.
Preparing to unpack .../58-libxpm4_1%3a3.5.12-1.1+deb12u1_amd64.deb ...
Unpacking libxpm4:amd64 (1:3.5.12-1.1+deb12u1) ...
Selecting previously unselected package libgd3:amd64.
Preparing to unpack .../59-libgd3_2.3.3-9_amd64.deb ...
Unpacking libgd3:amd64 (2.3.3-9) ...
Selecting previously unselected package libc-devtools.
Preparing to unpack .../60-libc-devtools_2.36-9+deb12u9_amd64.deb ...
Unpacking libc-devtools (2.36-9+deb12u9) ...
Selecting previously unselected package linux-libc-dev:amd64.
Preparing to unpack .../61-linux-libc-dev_6.1.128-1_amd64.deb ...
Unpacking linux-libc-dev:amd64 (6.1.128-1) ...
Selecting previously unselected package libcrypt-dev:amd64.
Preparing to unpack .../62-libcrypt-dev_1%3a4.4.33-2_amd64.deb ...
Unpacking libcrypt-dev:amd64 (1:4.4.33-2) ...
Selecting previously unselected package libtirpc-dev:amd64.
Preparing to unpack .../63-libtirpc-dev_1.3.3+ds-1_amd64.deb ...
Unpacking libtirpc-dev:amd64 (1.3.3+ds-1) ...
Selecting previously unselected package libnsl-dev:amd64.
Preparing to unpack .../64-libnsl-dev_1.3.0-2_amd64.deb ...
Unpacking libnsl-dev:amd64 (1.3.0-2) ...
Selecting previously unselected package rpcsvc-proto.
Preparing to unpack .../65-rpcsvc-proto_1.4.3-1_amd64.deb ...
Unpacking rpcsvc-proto (1.4.3-1) ...
Selecting previously unselected package libc6-dev:amd64.
Preparing to unpack .../66-libc6-dev_2.36-9+deb12u9_amd64.deb ...
Unpacking libc6-dev:amd64 (2.36-9+deb12u9) ...
Selecting previously unselected package manpages-dev.
Preparing to unpack .../67-manpages-dev_6.03-2_all.deb ...
Unpacking manpages-dev (6.03-2) ...
Setting up libexpat1:amd64 (2.5.0-1+deb12u1) ...
Setting up libaom3:amd64 (3.6.0-1+deb12u1) ...
Setting up libabsl20220623:amd64 (20220623.1-1) ...
Setting up libxau6:amd64 (1:1.0.9-1) ...
Setting up liblerc4:amd64 (4.0.0+ds-2) ...
Setting up manpages (6.03-2) ...
Setting up libbrotli1:amd64 (1.0.9-2+b6) ...
Setting up binutils-common:amd64 (2.40-2) ...
Setting up libdeflate0:amd64 (1.14-1) ...
Setting up linux-libc-dev:amd64 (6.1.128-1) ...
Setting up libctf-nobfd0:amd64 (2.40-2) ...
Setting up libsvtav1enc1:amd64 (1.4.1+dfsg-1) ...
Setting up libgomp1:amd64 (12.2.0-14) ...
Setting up libjbig0:amd64 (2.1-6.1) ...
Setting up librav1e0:amd64 (0.5.1-6) ...
Setting up libjansson4:amd64 (2.14-2) ...
Setting up libtirpc-dev:amd64 (1.3.3+ds-1) ...
Setting up rpcsvc-proto (1.4.3-1) ...
Setting up libjpeg62-turbo:amd64 (1:2.1.5-2) ...
Setting up libx11-data (2:1.8.4-2+deb12u2) ...
Setting up libmpfr6:amd64 (4.2.0-1) ...
Setting up libquadmath0:amd64 (12.2.0-14) ...
Setting up libpng16-16:amd64 (1.6.39-2) ...
Setting up libmpc3:amd64 (1.3.1-1) ...
Setting up libatomic1:amd64 (12.2.0-14) ...
Setting up fonts-dejavu-core (2.37-6) ...
Setting up libgav1-1:amd64 (0.18.0-1+b1) ...
Setting up libdav1d6:amd64 (1.0.0-2+deb12u1) ...
Setting up libwebp7:amd64 (1.2.4-0.2+deb12u1) ...
Setting up libubsan1:amd64 (12.2.0-14) ...
Setting up libnuma1:amd64 (2.0.16-1) ...
Setting up libnsl-dev:amd64 (1.3.0-2) ...
Setting up libcrypt-dev:amd64 (1:4.4.33-2) ...
Setting up libtiff6:amd64 (4.5.0-6+deb12u2) ...
Setting up libasan8:amd64 (12.2.0-14) ...
Setting up libtsan2:amd64 (12.2.0-14) ...
Setting up libbinutils:amd64 (2.40-2) ...
Setting up libisl23:amd64 (0.25-1.1) ...
Setting up libde265-0:amd64 (1.0.11-1+deb12u2) ...
Setting up libc-dev-bin (2.36-9+deb12u9) ...
Setting up libbsd0:amd64 (0.11.7-2) ...
Setting up libyuv0:amd64 (0.0~git20230123.b2528b0-1) ...
Setting up libcc1-0:amd64 (12.2.0-14) ...
Setting up liblsan0:amd64 (12.2.0-14) ...
Setting up libitm1:amd64 (12.2.0-14) ...
Setting up libctf0:amd64 (2.40-2) ...
Setting up manpages-dev (6.03-2) ...
Setting up libxdmcp6:amd64 (1:1.1.2-3) ...
Setting up cpp-12 (12.2.0-14) ...
Setting up libxcb1:amd64 (1.15-1) ...
Setting up libavif15:amd64 (0.11.1-1) ...
Setting up fontconfig-config (2.14.1-4) ...
debconf: unable to initialize frontend: Dialog
debconf: (TERM is not set, so the dialog frontend is not usable.)
debconf: falling back to frontend: Readline
debconf: unable to initialize frontend: Readline
debconf: (Can't locate Term/ReadLine.pm in @INC (you may need to install the Term::ReadLine module) (@INC contains: /etc/perl /usr/local/lib/x86_64-linux-gnu/perl/5.36.0 /usr/local/share/perl/5.36.0 /usr/lib/x86_64-linux-gnu/perl5/5.36 /usr/share/perl5 /usr/lib/x86_64-linux-gnu/perl-base /usr/lib/x86_64-linux-gnu/perl/5.36 /usr/share/perl/5.36 /usr/local/lib/site_perl) at /usr/share/perl5/Debconf/FrontEnd/Readline.pm line 7.)
debconf: falling back to frontend: Teletype
Setting up libgprofng0:amd64 (2.40-2) ...
Setting up libfreetype6:amd64 (2.12.1+dfsg-5+deb12u3) ...
Setting up libgcc-12-dev:amd64 (12.2.0-14) ...
Setting up libx265-199:amd64 (3.5-2+b1) ...
Setting up cpp (4:12.2.0-3) ...
Setting up libc6-dev:amd64 (2.36-9+deb12u9) ...
Setting up libx11-6:amd64 (2:1.8.4-2+deb12u2) ...
Setting up libfontconfig1:amd64 (2.14.1-4) ...
Setting up binutils-x86-64-linux-gnu (2.40-2) ...
Setting up libxpm4:amd64 (1:3.5.12-1.1+deb12u1) ...
Setting up libheif1:amd64 (1.15.1-1+deb12u1) ...
Setting up binutils (2.40-2) ...
Setting up gcc-12 (12.2.0-14) ...
Setting up libgd3:amd64 (2.3.3-9) ...
Setting up libc-devtools (2.36-9+deb12u9) ...
Setting up gcc (4:12.2.0-3) ...
Processing triggers for libc-bin (2.36-9+deb12u9) ...
Removing intermediate container 23346448fa1c
 ---> 92ed9630cd88
Step 4/9 : RUN pip install uv
 ---> Running in c75d00617acb
Collecting uv
  Downloading uv-0.5.30-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (11 kB)
Downloading uv-0.5.30-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (16.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.3/16.3 MB 41.1 MB/s eta 0:00:00
Installing collected packages: uv
Successfully installed uv-0.5.30
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 24.0 -> 25.0.1
[notice] To update, run: pip install --upgrade pip
Removing intermediate container c75d00617acb
 ---> 613374c11eee
Step 5/9 : COPY requirements.txt .
 ---> 6942d9e73c34
Step 6/9 : RUN uv pip install --system -r requirements.txt
 ---> Running in 78fbee408456
Using Python 3.11.11 environment at: /usr/local
Resolved 57 packages in 679ms
Downloading uvloop (3.8MiB)
Downloading aiohttp (1.6MiB)
Downloading psycopg2-binary (2.9MiB)
Downloading sqlalchemy (3.1MiB)
Downloading asyncpg (3.0MiB)
Downloading cryptography (4.0MiB)
Downloading pydantic-core (1.9MiB)
 Downloaded aiohttp
 Downloaded pydantic-core
 Downloaded psycopg2-binary
 Downloaded asyncpg
 Downloaded uvloop
 Downloaded cryptography
 Downloaded sqlalchemy
Prepared 57 packages in 853ms
Installed 57 packages in 80ms
 + aiohappyeyeballs==2.4.6
 + aiohttp==3.11.12
 + aioresponses==0.7.8
 + aiosignal==1.3.2
 + aiosqlite==0.21.0
 + annotated-types==0.7.0
 + anyio==4.8.0
 + asyncpg==0.30.0
 + attrs==25.1.0
 + bcrypt==4.0.1
 + certifi==2025.1.31
 + cffi==1.17.1
 + click==8.1.8
 + coverage==7.6.12
 + cryptography==44.0.1
 + ecdsa==0.19.0
 + fastapi==0.115.8
 + frozenlist==1.5.0
 + greenlet==3.1.1
 + h11==0.14.0
 + httpcore==1.0.7
 + httptools==0.6.4
 + httpx==0.28.1
 + idna==3.10
 + iniconfig==2.0.0
 + loguru==0.7.3
 + multidict==6.1.0
 + packaging==24.2
 + passlib==1.7.4
 + pluggy==1.5.0
 + propcache==0.2.1
 + psycopg2-binary==2.9.10
 + pyasn1==0.6.1
 + pycparser==2.22
 + pydantic==2.10.6
 + pydantic-core==2.27.2
 + pydantic-settings==2.7.1
 + pytest==8.3.4
 + pytest-asyncio==0.25.3
 + pytest-cov==6.0.0
 + pytest-mock==3.14.0
 + python-dotenv==1.0.1
 + python-jose==3.3.0
 + python-multipart==0.0.20
 + pyyaml==6.0.2
 + rsa==4.9
 + six==1.17.0
 + sniffio==1.3.1
 + sqlalchemy==2.0.38
 + sqlmodel==0.0.22
 + starlette==0.45.3
 + typing-extensions==4.12.2
 + uvicorn==0.34.0
 + uvloop==0.21.0
 + watchfiles==1.0.4
 + websockets==14.2
 + yarl==1.18.3
Removing intermediate container 78fbee408456
 ---> ca4e9b5e1ea0
Step 7/9 : COPY . .
 ---> 019d5a2d01a2
Step 8/9 : ENV PORT=8000
 ---> Running in b2eed7cc511e
Removing intermediate container b2eed7cc511e
 ---> 40a228f50b37
Step 9/9 : CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
 ---> Running in 08b9e8835935
Removing intermediate container 08b9e8835935
 ---> 1e972b16ba2f
Successfully built 1e972b16ba2f
Successfully tagged gcr.io/brite-450618/movie-backend:latest
PUSH
Pushing gcr.io/brite-450618/movie-backend
The push refers to repository [gcr.io/brite-450618/movie-backend]
c9822974ce83: Preparing
8650260a96ae: Preparing
7668a8f35096: Preparing
c0728ad5c0cc: Preparing
92c82614ac7a: Preparing
093ebd616959: Preparing
20769e22c821: Preparing
64ade5ba3927: Preparing
6d50ae87acc4: Preparing
7914c8f600f5: Preparing
20769e22c821: Waiting
64ade5ba3927: Waiting
093ebd616959: Waiting
6d50ae87acc4: Waiting
7914c8f600f5: Waiting
7668a8f35096: Pushed
093ebd616959: Pushed
20769e22c821: Layer already exists
64ade5ba3927: Layer already exists
6d50ae87acc4: Layer already exists
7914c8f600f5: Layer already exists
c0728ad5c0cc: Pushed
8650260a96ae: Pushed
c9822974ce83: Pushed
92c82614ac7a: Pushed
latest: digest: sha256:6c2233147677fa9eb19917ed822c3feda3b06fedce6a9ee3edc27b4ee13ccaf9 size: 2421
DONE
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ID                                    CREATE_TIME                DURATION  SOURCE                                                                                      IMAGES                                       STATUS
0fdc98cd-200a-4312-a6ab-829049eb1975  2025-02-11T20:53:49+00:00  1M31S     gs://brite-450618_cloudbuild/source/1739307201.750908-534e0ae3df7947ca947b84acd0d7c05a.tgz  gcr.io/brite-450618/movie-backend (+1 more)  SUCCESS
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