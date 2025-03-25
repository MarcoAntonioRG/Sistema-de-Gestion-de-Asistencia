# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos y luego instala las dependencias
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia el resto de los archivos del proyecto en el contenedor
COPY . .

# Exponer el puerto en el que la aplicación se ejecutará
EXPOSE 4000

CMD ["flask", "run"]