# 💻 Sistema de Gestión de Asistencia

Microservicio de gestión de asistencia de una aplicación web.

---

## Tecnologías Usadas

- Python
- Flask
- PostgreSQL
- Docker
- Postman

---

## Requisitos Técnicos

Para ejecutar la aplicación es necesario tener instalado en tu máquina local:

- Docker para la ejecución de todo el microservicio.
- Postman para utilizar y verificar las rutas de la API.

---

## Descripción

Aplicación web que funciona como "Middleware" y que permite subir el registro de asistencia de trabajadores obtenido del marcaje en reloj, en el cual se pueden corregir inconsistencias o errores de marcaje encontrados para así "limpiar" estos datos que luego son utilizados para el cálculo de horas trabajadas y la remuneración respectiva.

---

## Pasos para ejecutar

1. **Clonar el repositorio** del proyecto en tu máquina local:
   ```bash
   git clone https://github.com/MarcoAntonioRG/Sistema-de-Gestion-de-Asistencia.git
   cd Sistema-de-Gestion-de-Asistencia
   
2. Ejecutar microservicio con:
   ```bash
   docker-compose up -d

3. Ejecutar servicio de `app` con:
   ```bash
   docker-compose run app bash

4. Crear el directorio de migraciones:
   ```bash
   flask db init

5. Crear la migración inicial, o cada vez que se realize una modificación a la base de datos:
   ```bash
   flask db migrate -m "Migracion Inicial"

6. Aplicar la migración a la base de datos:
   ```bash
   flask db upgrade
