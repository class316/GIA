# Despliegue de GIA

GIA puede ejecutarse localmente para desarrollo y publicarse como sistema web en Render o Railway usando Django + Gunicorn + PostgreSQL.

## Variables de entorno

Configura estas variables en el panel del hosting:

```env
SECRET_KEY=clave-larga-y-segura
DEBUG=False
GIA_ALLOWED_HOSTS=gia-taller.onrender.com
CSRF_TRUSTED_ORIGINS=https://gia-taller.onrender.com
DATABASE_URL=postgresql://usuario:password@host:5432/base_de_datos
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

En Railway tambien puedes usar `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT` y `PGDATABASE` si tu servicio de PostgreSQL no entrega `DATABASE_URL`.

Para pruebas locales puedes dejar `DEBUG=True` y usar SQLite.

## Render

1. Sube el proyecto a GitHub.
2. Crea una base de datos PostgreSQL en Render.
3. Crea un Web Service y conecta el repositorio.
4. Usa estos comandos:

Build Command:

```bash
bash build.sh
```

Start Command:

```bash
gunicorn gia.wsgi:application
```

5. Agrega las variables de entorno.
6. Abre la URL publica generada por Render.

## Railway

1. Crea un proyecto desde GitHub.
2. Agrega PostgreSQL.
3. Configura las variables de entorno.
4. Usa `DATABASE_URL` o las variables `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`, `PGDATABASE`.
5. Usa el proceso web del `Procfile`:

```bash
web: gunicorn gia.wsgi:application
```

## Archivos estaticos y media

`collectstatic` se ejecuta en `build.sh`. Los archivos subidos por usuarios quedan en `MEDIA_ROOT`.

En produccion real, conviene mover `media/` a almacenamiento persistente o externo, por ejemplo S3, Cloudinary o un disco persistente del proveedor. En planes gratuitos, algunos proveedores pueden borrar archivos subidos al reiniciar el servicio.

## Datos existentes

Para migrar datos desde SQLite:

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > datos_gia.json
```

Luego en produccion:

```bash
python manage.py loaddata datos_gia.json
```

## Crear administrador

Si no cargas datos previos:

```bash
python manage.py createsuperuser
```

## Acceso movil y PWA

En internet, abre la URL publica desde el celular. En Chrome/Android usa "Agregar a pantalla principal". La app usa el mismo backend y la misma base de datos que el computador.

## Dominio propio

1. Compra un dominio.
2. En Render/Railway configura el dominio personalizado.
3. En el proveedor del dominio crea el registro DNS indicado por el hosting.
4. Agrega el dominio a:

```env
GIA_ALLOWED_HOSTS=gia-taller.onrender.com,www.tudominio.com,tudominio.com
CSRF_TRUSTED_ORIGINS=https://gia-taller.onrender.com,https://www.tudominio.com,https://tudominio.com
```
