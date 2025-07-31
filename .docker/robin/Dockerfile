FROM maven:3.9.9-amazoncorretto-21-debian

WORKDIR /usr/src/

RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/transilvlad/robin.git robin/

WORKDIR /usr/src/robin/

RUN mvn clean compile assembly:single && \
    cp target/robin-jar-with-dependencies.jar robin.jar

# Keep container running. This is probably unwise for a prod environment.
ENTRYPOINT ["tail", "-f", "/dev/null"]
