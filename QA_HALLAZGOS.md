# Informe de hallazgos de QA — GIA

**Proyecto:** GIA — Sistema de Gestión Integral Automotriz
**Tipo:** Registro inicial de hallazgos y oportunidades de mejora
**Fecha:** 19 de octubre de 2026
**Estado:** Borrador; varios puntos requieren reproducción y validación.

## 1. Objetivo y alcance

Este documento organiza las observaciones hechas durante una exploración funcional de GIA. Se basa en notas del usuario, capturas compartidas y el resultado de las pruebas automatizadas. No se ha inspeccionado el código para confirmar la causa de cada hallazgo y no todos los puntos deben considerarse defectos confirmados.

Se ejecutó:

```powershell
python manage.py test --verbosity 2
```

**Resultado reportado:** 24 pruebas aprobadas, 0 fallidas, en 8,2 segundos. Django indicó que la comprobación del sistema no tenía problemas. Esto valida los escenarios cubiertos por esas pruebas, no toda la aplicación.

## 2. Estados utilizados

- **Observado:** comportamiento reportado durante la exploración.
- **Pendiente de reproducir:** requiere una prueba controlada para confirmarlo.
- **Mejora propuesta:** requisito deseado que debe contrastarse con la implementación actual.
- **Prioridad sugerida:** estimación inicial; confirmar según impacto y frecuencia.

## 3. Registro de hallazgos

### GIA-QA-001 — Opciones del menú no visibles al 100 % de zoom
- **Área:** Interfaz y navegación.
- **Observación:** las capturas muestran Cotizaciones, Gastos y Auditoría al 80 % de zoom; el usuario indica que dejan de verse en la zona visible al 100 %.
- **Esperado:** las opciones deben ser accesibles con el zoom normal y tamaños de ventana habituales, sin exigir cambiar el zoom.
- **Evidencia:** capturas al 80 % y 100 %.
- **Estado:** observado; falta confirmar si es recorte, desplazamiento u otro comportamiento.
- **Prioridad sugerida:** alta.

### GIA-QA-002 — Cierre de sesión compartido entre pestañas
- **Área:** Autenticación y sesiones.
- **Observación:** cerrar sesión en una pestaña cierra la sesión en las demás pestañas del mismo navegador.
- **Esperado:** confirmar el requisito. Compartir sesión entre pestañas suele ser normal; se debe comprobar si afecta solo a la misma cuenta o también a cuentas diferentes.
- **Estado:** comportamiento observado, no clasificado todavía como defecto confirmado.
- **Prioridad:** por determinar.

### GIA-QA-003 — Registro de clientes controlado por administración
- **Área:** Usuarios y permisos.
- **Requisito:** el cliente no debería registrarse por su cuenta; la cuenta la crea el administrador.
- **Esperado:** permitir el alta mediante el flujo autorizado y bloquear registros no autorizados.
- **Estado:** requisito propuesto; validar el comportamiento actual.
- **Prioridad sugerida:** media.

### GIA-QA-004 — Registro de vehículos por clientes y mecánicos
- **Área:** Vehículos y permisos.
- **Requisito:** el cliente registra marca, modelo, año y placa de su vehículo. El mecánico registra esos datos y además selecciona al cliente propietario.
- **Esperado:** cada formulario solicita los datos pertinentes y vincula correctamente el vehículo con su propietario.
- **Estado:** requisito definido; pendiente de contrastar con la implementación.
- **Prioridad sugerida:** alta.

### GIA-QA-005 — Validación del formato de placa
- **Área:** Vehículos y validaciones.
- **Requisito:** validar placas colombianas de tres letras y tres números.
- **Esperado:** aplicar la regla a las categorías de vehículos contempladas y mostrar un mensaje claro si no cumple.
- **Estado:** pendiente de confirmar qué categorías admite GIA antes de fijar la regla definitiva.
- **Prioridad sugerida:** media.

### GIA-QA-006 — Acceso a cotizaciones
- **Área:** Cotizaciones y navegación.
- **Observación:** el usuario informa que no logra ver las cotizaciones y que en una pantalla parecía mostrarse únicamente el botón de cerrar sesión.
- **Esperado:** usuarios autorizados pueden consultar las cotizaciones que les corresponden, con navegación visible y permisos correctos.
- **Estado:** pendiente de reproducir y localizar por perfil.
- **Prioridad sugerida:** alta.

### GIA-QA-007 — Visibilidad de cotizaciones para el taller
- **Área:** Cotizaciones y flujo de trabajo.
- **Requisito propuesto:** administración y mecánicos deberían consultar cotizaciones dirigidas al taller para coordinar la atención y quién puede asumir el trabajo.
- **Esperado:** acceso y acciones según roles; no todos deben poder aceptar o modificar cualquier cotización.
- **Estado:** mejora propuesta; definir permisos y flujo.
- **Prioridad sugerida:** alta.

### GIA-QA-008 — Protección de la cuenta principal
- **Área:** Usuarios y seguridad.
- **Requisito:** la cuenta principal no debe poder ser eliminada por otro administrador ni por cuentas creadas desde ella.
- **Esperado:** protección aplicada en el servidor, no solo ocultando un botón.
- **Estado:** pendiente de identificar cómo se determina la cuenta principal.
- **Prioridad sugerida:** alta.

### GIA-QA-009 — Prevención de autoeliminación de cuentas
- **Área:** Usuarios y seguridad.
- **Requisito propuesto:** impedir que un usuario elimine accidentalmente su propia cuenta.
- **Esperado:** bloquear la autoeliminación o definir un flujo administrativo seguro y trazable.
- **Estado:** validar reglas actuales.
- **Prioridad sugerida:** media.

### GIA-QA-010 — Mostrar y ocultar contraseña al crear usuarios
- **Área:** Usabilidad y formularios.
- **Observación:** falta un control de ojo para mostrar y verificar la contraseña introducida.
- **Esperado:** alternar entre contraseña visible y oculta sin cambiar el valor.
- **Estado:** mejora solicitada; revisar formularios de creación.
- **Prioridad sugerida:** baja.

### GIA-QA-011 — Trabajo asignado a mecánicos inactivos
- **Área:** Órdenes y personal.
- **Observación:** el usuario indica que no debería permitirse asignar o ejecutar trabajo si el mecánico está inactivo.
- **Esperado:** impedir la asignación o el inicio del trabajo conforme a la regla de negocio.
- **Estado:** pendiente de reproducir y precisar la acción.
- **Prioridad sugerida:** alta.

### GIA-QA-012 — Herramienta que permanece «en uso» tras finalizar servicio
- **Área:** Herramientas y órdenes.
- **Observación:** después de finalizar un servicio del mecánico Diego, una herramienta seguía como «en uso»; al revisar más tarde aparecía disponible.
- **Esperado:** al finalizar la tarea, los recursos deben quedar en el estado correcto según las reglas de uso.
- **Evidencia:** reporte del usuario; comportamiento intermitente.
- **Estado:** pendiente de reproducir; no confirmado hasta obtener pasos repetibles o registros.
- **Prioridad sugerida:** alta si impide utilizar herramientas disponibles.

### GIA-QA-013 — Modificación de tareas finalizadas
- **Área:** Órdenes de trabajo.
- **Requisito:** una tarea finalizada no debería poder modificarse.
- **Esperado:** bloquear modificaciones operativas; cualquier corrección administrativa debe tener un flujo controlado y auditable.
- **Estado:** definir qué campos y acciones deben bloquearse.
- **Prioridad sugerida:** alta.

### GIA-QA-014 — Cambio de estado sin mecánico asignado
- **Área:** Órdenes de trabajo.
- **Observación:** aparentemente se puede cambiar el estado de una orden sin mecánico asignado.
- **Esperado:** permitir únicamente transiciones válidas cuando no hay asignación.
- **Estado:** pendiente de reproducir y definir transiciones permitidas.
- **Prioridad sugerida:** alta.

### GIA-QA-015 — Modificación de pedidos cancelados
- **Área:** Órdenes o pedidos.
- **Requisito:** un pedido cancelado no debería admitir modificaciones operativas.
- **Esperado:** bloquear cambios incompatibles con la cancelación y conservar trazabilidad de acciones administrativas permitidas.
- **Estado:** definir tipo de pedido y excepciones.
- **Prioridad sugerida:** alta.

### GIA-QA-016 — Acceso de mecánicos a servicios, repuestos y herramientas
- **Área:** Navegación y permisos.
- **Requisito propuesto:** los mecánicos deben consultar las secciones de servicios, repuestos y herramientas que necesitan.
- **Esperado:** mostrar opciones relevantes al rol y aplicar permisos adecuados a cada operación.
- **Estado:** comprobar qué secciones faltan y cuáles ya son accesibles.
- **Prioridad sugerida:** alta.

### GIA-QA-017 — Acceso al módulo de gastos
- **Área:** Gestión administrativa y navegación.
- **Observación:** se informó que el módulo de gastos no se veía. Una captura posterior lo muestra al 80 % de zoom; falta confirmar su visibilidad al 100 %.
- **Esperado:** módulo visible para los perfiles autorizados y accesible según permisos.
- **Estado:** relacionado con GIA-QA-001; pendiente de validar al zoom normal y por rol.
- **Prioridad sugerida:** alta para responsables contables.

### GIA-QA-018 — Conservación y consulta histórica de gastos
- **Área:** Gastos y trazabilidad contable.
- **Requisito:** evitar la eliminación ordinaria de gastos y permitir consultas por hora, día, fecha y mes para facilitar el arqueo mensual.
- **Esperado:** conservar historial verificable y filtros por período; correcciones o anulaciones deben mantener trazabilidad.
- **Evidencia:** una captura de auditoría muestra una acción `eliminacion_registro` relacionada con Gastos; se debe comprobar el flujo y los permisos.
- **Estado:** mejora propuesta con indicio en la evidencia.
- **Prioridad sugerida:** alta.

### GIA-QA-019 — Acceso al módulo de auditoría
- **Área:** Seguridad y navegación.
- **Observación:** inicialmente se informó que no se veía. Las capturas posteriores muestran la auditoría abierta y mensajes de cadena válida y hashes coincidentes.
- **Esperado:** módulo accesible para perfiles autorizados y presentación correcta de la información.
- **Estado:** funciona en la evidencia aportada; falta validar su visibilidad en el menú al 100 %. La pantalla no equivale a una auditoría integral de seguridad.
- **Prioridad sugerida:** media-alta.

### GIA-QA-020 — Centrado del vehículo en la pantalla de acceso
- **Área:** Interfaz adaptable.
- **Requisito:** la imagen del vehículo debe permanecer centrada al cambiar el tamaño de la página o ventana.
- **Esperado:** centrado consistente en los tamaños contemplados y sin desbordamientos.
- **Estado:** mejora visual pendiente de validar.
- **Prioridad sugerida:** baja.

### GIA-QA-021 — Política para crear administradores adicionales
- **Área:** Usuarios y seguridad.
- **Observación:** se plantea revisar si conviene permitir otros administradores; el usuario indicó que no es prioritario.
- **Esperado:** definir una política explícita de creación y permisos.
- **Estado:** análisis pendiente; no es defecto confirmado.
- **Prioridad sugerida:** baja.

## 4. Resumen de pruebas automatizadas

**Comando:** `python manage.py test --verbosity 2`

- Pruebas encontradas: 24.
- Aprobadas: 24.
- Fallidas: 0.
- Duración: 8,2 segundos.
- Comprobación de Django: sin problemas.

Las pruebas incluyen escenarios de inventario, permisos de órdenes, formularios, costos y estados de repuestos. Conviene volver a ejecutar la suite después de cada cambio y guardar los resultados.

## 5. Próximos pasos

1. Reproducir los hallazgos pendientes usando datos de prueba.
2. Adjuntar capturas y pasos exactos a cada hallazgo confirmado.
3. Asignar severidad y prioridad según impacto y frecuencia.
4. Corregir los defectos priorizados en una iteración posterior.
5. Ejecutar pruebas de regresión tras las correcciones.

## 6. Nota para lectores

Este documento registra observaciones y requisitos propuestos durante una exploración funcional. No todos los puntos se han reproducido ni verificado mediante inspección del código. Los estados deben actualizarse cuando exista evidencia adicional.
