FROM openjdk:8-jre-slim

# Instalar Python (necesario para las extensions)
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar todo el proyecto
COPY . .

EXPOSE 9933 8080

# Comando para iniciar SmartFoxServer (ajusta si la ruta es diferente)
CMD ["java", "-jar", "SFS2X/smartfoxserver2x.jar"]
