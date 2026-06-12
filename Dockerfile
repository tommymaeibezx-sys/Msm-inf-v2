FROM amazoncorretto:8

# Instalar dependencias básicas
RUN yum install -y python3 curl unzip && yum clean all

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Dar permisos de ejecución al .jar (por si acaso)
RUN chmod +x sfs2x/smartfoxserver2x.jar

# Exponer puertos de SmartFoxServer
EXPOSE 9933 8080 8443

# Comando de inicio
CMD ["java", "-jar", "sfs2x/smartfoxserver2x.jar"]
