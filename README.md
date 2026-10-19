# GIA — Sistema de Gestión Integral Automotriz

GIA es una aplicación web desarrollada con Django para apoyar la gestión de las operaciones de un taller automotriz.

## Tecnologías

- Python
- Django
- SQLite para desarrollo local, según la configuración del entorno
- PostgreSQL y Gunicorn contemplados en las dependencias de despliegue
- HTML, CSS y plantillas de Django

## Módulos del proyecto

El código está organizado en aplicaciones Django relacionadas con:

- Clientes
- Vehículos
- Mecánicos
- Órdenes de servicio
- Cotizaciones
- Repuestos
- Herramientas
- Gastos
- Usuarios y roles
- Auditoría

La disponibilidad y el alcance de cada función deben verificarse en la aplicación.

## Requisitos previos

- Python compatible con las dependencias del proyecto.
- Git.
- PowerShell en Windows para los comandos siguientes.

## Instalación local en Windows

Clona el repositorio o descarga el código y abre PowerShell en la carpeta del proyecto.

Crea un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Aplica las migraciones:

```powershell
python manage.py migrate
```

Crea un usuario administrador local:

```powershell
python manage.py createsuperuser
```

Inicia el servidor de desarrollo:

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador.

> Si el proyecto requiere variables de entorno adicionales, configura los valores apropiados a partir de `.env.example` y de la documentación de despliegue. No uses secretos de producción en desarrollo.

## Pruebas automatizadas

Ejecuta:

```powershell
python manage.py test --verbosity 2
```

En una ejecución registrada el 19 de octubre de 2026 se reportaron 24 pruebas aprobadas. Ejecuta las pruebas nuevamente en tu entorno para confirmar el estado actual.

## Calidad y documentación QA

Consulta `QA_HALLAZGOS.md` para revisar los hallazgos y oportunidades de mejora documentados durante las pruebas.

## Despliegue

Consulta `README_DEPLOY.md` para conocer la configuración de despliegue contemplada por el proyecto. La presencia de esta documentación no implica que exista un despliegue público activo.

## Seguridad

- No publiques archivos `.env`, bases de datos locales, credenciales ni datos personales.
- Configura una clave secreta propia y variables de entorno adecuadas para cada ambiente.
- Revisa las credenciales predeterminadas utilizadas en la creación de cuentas antes de utilizar el sistema en un entorno real.

## Estado del proyecto

Proyecto en desarrollo y revisión de calidad. La documentación QA registra aspectos por corregir o validar; no todos los módulos ni escenarios deben considerarse verificados.
