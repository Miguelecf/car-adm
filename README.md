# car-adm / EasyTaxi

> README recruiter-oriented en español, basado en la evidencia disponible actualmente en el repositorio.

## 1. Título del proyecto

**car-adm / EasyTaxi**

Sistema web monolítico para la **gestión operativa de una flota de autos y su relación con choferes, contratos, cobros, mantenimiento, documentación e incidentes**.

## 2. Resumen ejecutivo

Se pudo confirmar que este repositorio implementa una aplicación web construida con **FastAPI + Jinja2 + SQLAlchemy + SQLite**, con interfaz en español y navegación enriquecida con **HTMX**. El sistema está orientado a administrar autos, choferes, contratos, cobros semanales, servicios, documentos e incidentes.

Por naming, textos del dashboard y estructura funcional, **parece indicar** un caso de uso asociado a una operación tipo taxi, remis o movilidad urbana. Aun así, **no hay evidencia suficiente para afirmar con precisión** la vertical comercial exacta más allá de la administración de flota y choferes.

## 3. Problema real que resuelve

La aplicación centraliza información que normalmente podría quedar dispersa en planillas, mensajes o seguimiento manual:

- estado de los vehículos,
- datos de choferes,
- contratos activos y finalizados,
- cobros semanales y pagos pendientes,
- mantenimientos,
- vencimientos documentales,
- incidentes como multas, accidentes o reclamos.

La interpretación más defensible es que el proyecto busca resolver la **gestión administrativa y operativa diaria de una pequeña flota**, ayudando a responder rápidamente:

- qué autos están activos,
- qué chofer tiene asignada cada unidad,
- cuánto se cobró y qué falta cobrar,
- qué documentación vence pronto,
- qué vehículos requieren servicio,
- qué incidentes siguen pendientes.

## 4. Cómo la aplicación resuelve ese problema

La solución está implementada como una aplicación web server-rendered con módulos separados por dominio:

1. **Dashboard operativo** con KPIs de flota, contratos, cobros, alertas, próximos mantenimientos, documentos por vencer y una vista simple de rentabilidad por auto.
2. **Gestión de autos** con alta, listado, edición y baja lógica, incluyendo estado del vehículo (`activo`, `en_taller`, `fuera_servicio`).
3. **Gestión de choferes** con alta, listado, edición y baja lógica, incluyendo datos personales y de licencia.
4. **Gestión de contratos** que vincula auto + chofer + fechas + km + monto semanal + depósito, con estado activo o finalizado.
5. **Gestión de cobros** con registro manual, marcado de pago realizado y generación de cobros semanales para contratos activos.
6. **Mantenimiento** con registro de servicios y seguimiento del próximo control por fecha o kilometraje.
7. **Documentación** con registro de documentos por vehículo y clasificación visual según vigencia.
8. **Incidentes** con alta de multa, accidente o reclamo, y resolución de pendientes.

También se pudo confirmar que buena parte de la UX se apoya en **HTMX**, evitando una SPA completa y manteniendo una interacción dinámica sobre templates HTML.

## 5. Qué construí como desarrollador/a

- Diseñé y desarrollé un **backoffice web completo** para administración de flota, contratos y cobranzas.
- Modelé entidades de negocio para **vehículos, choferes, contratos, pagos, mantenimientos, documentos e incidentes**.
- Implementé una **arquitectura por capas** con routers, servicios, modelos y templates.
- Construí CRUDs operativos para los módulos principales.
- Implementé **soft delete reutilizable** con trazabilidad (`deleted_at`, `deleted_by`, `delete_reason`).
- Agregué una rutina de compatibilidad para **SQLite** que incorpora columnas de soft delete sin destruir datos existentes.
- Desarrollé un **dashboard con métricas y alertas operativas** calculadas desde la capa de servicios.
- Incorporé validación server-side de fechas en formato **`dd/mm/yyyy`** con manejo explícito de error.
- Preparé **datos sintéticos de demo** orientados a Argentina/Buenos Aires para poblar el sistema sin hard deletes.
- Añadí **tests automatizados** enfocados en el comportamiento de soft delete sobre vehículos y choferes.

## 6. Stack tecnológico

### Backend
- Python
- FastAPI
- SQLAlchemy 2
- Pydantic
- pydantic-settings

### Frontend / UI
- Jinja2
- HTMX
- Tailwind CSS vía CDN
- Font Awesome
- Flatpickr con localización en español

### Base de datos
- SQLite

### Testing
- unittest

### Tooling / ejecución
- Uvicorn
- python-multipart

### Infraestructura
No se pudo confirmar despliegue, Docker, CI/CD, reverse proxy ni infraestructura declarativa.

## 7. Arquitectura y estructura del proyecto

La estructura visible responde a un monolito bien separado:

- `app/main.py`: punto de entrada, creación de app, registro de routers y startup.
- `app/core/`: configuración y base de datos.
- `app/models/`: modelos ORM y mixin de soft delete.
- `app/services/`: lógica de negocio por dominio.
- `app/routers/`: endpoints HTTP y conexión con formularios/templates.
- `app/web/templates/`: layout base y vistas HTML por módulo.
- `app/utils/`: utilidades, especialmente parseo y validación de fechas.
- `scripts/seed_argentina.py`: carga de datos demo sintéticos.
- `tests/`: tests automatizados disponibles.

También existe `app/schemas/`, pero con la evidencia actual **no se puede afirmar** que haya una capa de schemas Pydantic madura dentro de ese directorio.

## 8. Flujos principales del sistema

### Alta y administración de vehículos
Permite crear, listar, editar y eliminar lógicamente vehículos con marca, modelo, año, matrícula, color, kilometraje y estado.

### Alta y administración de choferes
Permite registrar choferes, editar su información y eliminarlos lógicamente, incluyendo datos de licencia.

### Creación de contratos entre auto y chofer
Cada contrato conecta vehículo y chofer con fechas, km inicial/final, monto semanal, depósito y estado.

### Gestión de cobros semanales
Se pueden registrar cobros, generar cobros semanales para contratos activos, marcar pagos realizados y consultar pendientes.

### Seguimiento de mantenimiento
Permite registrar servicios y definir próximo control por fecha o kilometraje.

### Seguimiento documental
Permite registrar documentos por auto y clasificarlos visualmente según su vencimiento.

### Registro y resolución de incidentes
Permite registrar multas, accidentes y reclamos, además de marcar incidentes como resueltos.

### Monitoreo desde el dashboard
Concentra KPIs, alertas, cobros pendientes, vencimientos y una estimación simple de rentabilidad por vehículo.

## 9. Capturas recomendadas para portfolio

### 1. Dashboard principal
- **Qué mostrar:** KPIs, alertas, próximos servicios, documentos por vencer, cobros pendientes y rentabilidad.
- **Por qué aporta valor:** resume negocio, lógica y visualización en una sola vista.
- **Qué mensaje transmite:** “Construí una solución con foco operativo real”.

### 2. Pantalla de contratos
- **Qué mostrar:** tabla con auto, chofer, fecha de inicio, km, monto semanal y estado.
- **Por qué aporta valor:** evidencia relación entre entidades y reglas de negocio.
- **Qué mensaje transmite:** “Sé modelar procesos administrativos con datos conectados”.

### 3. Pantalla de cobros
- **Qué mostrar:** listado con estados, acción de generar semanal y marcado de pago.
- **Por qué aporta valor:** muestra automatización y seguimiento financiero.
- **Qué mensaje transmite:** “Implementé procesos recurrentes y control de deuda/pago”.

### 4. Pantalla de documentos o mantenimiento
- **Qué mostrar:** vencimientos, próximos servicios y estados de alerta.
- **Por qué aporta valor:** demuestra enfoque preventivo, no solo carga de datos.
- **Qué mensaje transmite:** “Pensé el sistema para operación diaria”.

### 5. Formulario de alta/edición
- **Qué mostrar:** formulario de contrato, chofer o pago con datepicker y validaciones.
- **Por qué aporta valor:** evidencia cuidado por UX y consistencia de entrada de datos.
- **Qué mensaje transmite:** “También trabajé experiencia de uso y validación”.

## 10. Aprendizajes técnicos

- Separar HTTP, lógica de negocio y persistencia mejora mantenibilidad.
- FastAPI puede aprovecharse muy bien como backend HTML server-rendered.
- HTMX permite lograr dinamismo sin asumir la complejidad de una SPA completa.
- El soft delete bien implementado mejora auditoría y evita pérdida destructiva de datos.
- En SQLite, `create_all()` no reemplaza migraciones formales.
- Estandarizar fechas en `dd/mm/yyyy` obliga a resolver validación y feedback del lado servidor.

## 11. Aprendizajes profesionales

- Traducir una necesidad operativa en módulos concretos mejora la narrativa de impacto.
- Un proyecto gana valor para portfolio cuando refleja **flujo real**, no solo CRUD genérico.
- Preparar datos demo consistentes mejora mucho la presentación del producto.
- De cara a recruiters, este proyecto se comunica mejor como **herramienta de gestión operativa de flota y cobranzas**.

## 12. Próximos pasos para mejorar el proyecto

### Para portfolio / README
- Añadir screenshots reales del producto.
- Incluir GIFs o capturas de flujos con HTMX.
- Documentar con claridad qué módulos tienen edición completa y cuáles no.
- Incorporar una sección visual de “caso de uso” al inicio del README.

### Para CV / LinkedIn
- Resaltar arquitectura por capas, dashboard operativo, automatización de cobros semanales y soft delete auditable.
- Posicionarlo como proyecto de **gestión administrativa/operativa para flota**.

### Para entrevistas
- Preparar explicación de por qué se eligió FastAPI + Jinja2 + HTMX.
- Explicar cómo funciona el soft delete y la compatibilidad con SQLite.
- Tener lista una mejora propuesta hacia producción: auth, migraciones, más tests, persistencia de settings.

### Para el producto técnico
- Incorporar migraciones formales.
- Persistir ajustes en base de datos en vez de mantenerlos solo en memoria.
- Añadir autenticación y roles si el objetivo fuera multiusuario.
- Completar CRUD homogéneo donde todavía falte.
- Ampliar cobertura de tests en servicios, routers y reglas de negocio.

## 13. Limitaciones o aspectos no confirmados

- No hay evidencia suficiente de autenticación, autorización o manejo de usuarios.
- No se pudo confirmar despliegue, Docker, CI/CD ni monitoreo.
- No se pudo confirmar una API pública orientada a JSON; lo visible está centrado en HTML server-rendered.
- No se pudo confirmar almacenamiento real de archivos para documentos.
- No se observaron migraciones formales tipo Alembic.
- La configuración de `PAYMENT_DAY` parece actualizarse en memoria, no persistirse en base de datos.
- La cobertura de tests es acotada según la evidencia actual.
- El branding “EasyTaxi” sugiere una vertical específica, pero **no hay evidencia suficiente** para afirmarla con exactitud.

## 14. Resumen breve para CV o LinkedIn

Desarrollé una aplicación web de gestión operativa para flota de vehículos y choferes usando **FastAPI, SQLAlchemy, Jinja2, HTMX y SQLite**. Implementé módulos de **autos, choferes, contratos, cobros semanales, mantenimiento, documentos e incidentes**, además de un **dashboard con alertas y métricas operativas**. También incorporé **soft delete auditable**, validación server-side de fechas y datos demo para exhibición funcional del sistema.

## 15. Elevator pitch para entrevista

Construí una aplicación web para administrar una flota de autos y su operación diaria: contratos, cobros semanales, mantenimiento, documentación e incidentes.

La resolví como un monolito en FastAPI con Jinja2 y HTMX, para tener una experiencia dinámica sin depender de una SPA completa.

Uno de los puntos más valiosos fue separar la lógica en servicios y sumar soft delete auditable para evitar pérdida de información.

Además, desarrollé un dashboard que concentra alertas, cobros pendientes y una estimación simple de rentabilidad por vehículo.

## Cómo ejecutar el proyecto

> Esta sección se basa en la estructura y archivos actualmente disponibles en el repositorio.

### Requisitos
- Python 3.10+ recomendado
- Entorno virtual

### Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecución

```bash
uvicorn app.main:app --reload
```

### Datos demo

```bash
python scripts/seed_argentina.py
```

### Tests disponibles

```bash
python -m unittest tests.test_soft_delete
```

## Evidencia clave utilizada

- `app/main.py`
- `app/core/config.py`
- `app/core/database.py`
- `app/models/vehicle.py`
- `app/models/driver.py`
- `app/models/contract.py`
- `app/models/payment.py`
- `app/models/maintenance.py`
- `app/models/document.py`
- `app/models/incident.py`
- `app/services/vehicle_service.py`
- `app/services/driver_service.py`
- `app/services/contract_service.py`
- `app/services/payment_service.py`
- `app/services/maintenance_service.py`
- `app/services/document_service.py`
- `app/services/incident_service.py`
- `app/services/dashboard_service.py`
- `app/routers/vehicles.py`
- `app/routers/drivers.py`
- `app/routers/contracts.py`
- `app/routers/payments.py`
- `app/routers/maintenance.py`
- `app/routers/documents.py`
- `app/routers/incidents.py`
- `app/routers/dashboard.py`
- `app/routers/settings.py`
- `app/web/templates/layouts/base.html`
- `app/web/templates/pages/dashboard.html`
- `app/utils/dates.py`
- `scripts/seed_argentina.py`
- `tests/test_soft_delete.py`
