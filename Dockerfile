# syntax=docker/dockerfile:1

# ---------- Stage 1: build the executable JAR ----------
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# Resolve dependencies first so this layer is cached until pom.xml changes
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
RUN mvn -B -q clean package -DskipTests

# ---------- Stage 2: slim runtime image ----------
FROM eclipse-temurin:21-jre-alpine

LABEL org.opencontainers.image.title="calculator-devops" \
      org.opencontainers.image.description="Calculator REST API (Spring Boot)" \
      org.opencontainers.image.source="https://github.com/nikunj169/calculator-devops"

# Run as an unprivileged user
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app

COPY --from=build --chown=app:app /workspace/target/calculator.jar app.jar

USER app
EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/actuator/health | grep -q '"status":"UP"' || exit 1

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
