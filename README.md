# Sistema de Gestión de Asistencia

Aplicación web que funciona como "Middleware" y que permite subir el registro de asistencia de trabajadores obtenido del marcaje en reloj, en el cual se pueden corregir inconsistencias o errores de marcaje encontrados para así "limpiar" estos datos que luego son utilizados para el cálculo de horas trabajadas y la remuneración respectiva.

# Como ejecutar

1. Ejecutar contenedor con:
    
        docker compose up -d

2. Ejecutar servicio de `app` con:

        docker compose run app bash

3. Crear el directorio de migraciones:

        flask db init

4. Crear una migración inicial o cada vez que se realize una modificación a la base de datos:

        flask db migrate -m "Mensaje"

5. Aplicar la migración a la base de datos:
    
        flask db upgrade