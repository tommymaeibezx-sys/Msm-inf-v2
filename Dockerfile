FROM amazoncorretto:8

RUN yum install -y python3 curl && yum clean all

WORKDIR /app

COPY . .

EXPOSE 9933 8080

CMD ["java", "-jar", "sfs2x/smartfoxserver2x.jar"]
