# calculator-devops

A small Calculator REST API (Java 21, Spring Boot 3, Maven) wrapped in a fully
automated CI/CD pipeline: **GitHub → Jenkins → Docker Hub → Docker Compose**.
A push to `main` is picked up by Jenkins, built, tested, containerised, pushed
to Docker Hub and deployed behind an Nginx reverse proxy with no manual steps.

CSE 816 Software Production Engineering, Mini-Project.

| | |
|---|---|
| GitHub | https://github.com/nikunj169/calculator-devops |
| Docker Hub | https://hub.docker.com/r/niki9937/calculator-devops |

## API

| Operation | Endpoint | Behaviour |
|---|---|---|
| Add | `GET /api/v1/add?a=&b=` | `a + b` |
| Subtract | `GET /api/v1/subtract?a=&b=` | `a - b` |
| Multiply | `GET /api/v1/multiply?a=&b=` | `a * b` |
| Divide | `GET /api/v1/divide?a=&b=` | `a / b`; `b=0` → HTTP 400 |
| Health | `GET /actuator/health` | `{"status":"UP"}` |

Success:

```console
$ curl "localhost:8090/api/v1/add?a=2&b=3"
{"operation":"add","a":2,"b":3,"result":5}
```

Errors (missing, non-numeric or non-finite parameters, division by zero) return
HTTP 400 with a structured body:

```console
$ curl "localhost:8090/api/v1/divide?a=5&b=0"
{"timestamp":"2026-10-29T17:26:38.541Z","status":400,"error":"Bad Request","message":"Division by zero is not allowed","path":"/api/v1/divide"}
```

## Build, test, run

Requires JDK 21+ and Maven 3.9+ (or just Docker).

```bash
mvn clean package -DskipTests      # build target/calculator.jar
mvn test                           # unit + MockMvc integration tests -> target/surefire-reports/*.xml
java -jar target/calculator.jar    # run on :8080
```

### Docker

```bash
docker build -t niki9937/calculator-devops .
docker run -d -p 8085:8080 niki9937/calculator-devops
curl "localhost:8085/api/v1/multiply?a=6&b=7"
```

The `Dockerfile` is multi-stage: a `maven:3.9-eclipse-temurin-21` stage resolves
dependencies (cached layer) and builds the JAR; the runtime stage is
`eclipse-temurin:21-jre-alpine`, runs as a non-root user, exposes 8080 and has a
`HEALTHCHECK` on `/actuator/health`.

### Docker Compose (full stack)

```bash
docker compose up -d --wait        # 2 API replicas + Nginx on :8090
docker compose ps
curl "localhost:8090/api/v1/subtract?a=10&b=4"
docker compose down
```

```
            :8090
  client ──────────► nginx ──┬──► calculator (replica 1) :8080
                             └──► calculator (replica 2) :8080
                 calculator-net (bridge)
```

Nginx resolves the `calculator` service through Docker DNS on every request, so
it load-balances across replicas and follows them across redeploys. Both
services have health checks and `restart: unless-stopped`; Nginx only starts
once the API replicas are healthy. Override `IMAGE_TAG` / `PROXY_PORT` to pin
an image version or change the port.

## CI/CD pipeline (Jenkins)

`Jenkinsfile` (declarative):

| Stage | What it does |
|---|---|
| Checkout | `checkout scm` from GitHub |
| Build | `mvn -B clean package -DskipTests` |
| Test | `mvn -B test`; JUnit XML published; failures fail the build |
| Docker Build | image tagged `:<BUILD_NUMBER>` and `:latest` |
| Push | Docker Hub login from the Jenkins credential `dockerhub-credentials`, push both tags |
| Deploy | `docker compose up -d --wait`, then health + smoke check through Nginx |

Post actions email the build status (success/failure) and prune dangling images.

**Trigger:** `githubPush()` for a GitHub webhook, with `pollSCM('H/2 * * * *')`
as a fallback because the Jenkins used here runs on `localhost` and is not
reachable by GitHub.

**Re-runnable:** the Compose project name is fixed, so a re-run only recreates
containers whose image changed and leaves the rest running.

### Jenkins setup

1. Plugins: Pipeline, Git, GitHub, Credentials Binding, JUnit, Email Extension, Timestamper.
2. Credentials → add *Username with password* with ID `dockerhub-credentials` (Docker Hub user + access token).
3. Email: *Manage Jenkins → System → Extended E-mail Notification* → SMTP server.
   For Gmail use `smtp.gmail.com:465`, SSL, and an app password stored as a
   credential. (The demo machine uses a local [Mailpit](https://mailpit.axllent.org/)
   SMTP server on `localhost:1025` with its inbox at `localhost:8025`.)
4. New Item → *Pipeline* → *Pipeline script from SCM* → Git
   `https://github.com/nikunj169/calculator-devops.git`, branch `*/main`, script path `Jenkinsfile`.
5. (Optional) GitHub repo → Settings → Webhooks → `https://<public-jenkins>/github-webhook/`.

## Repository layout

```
calculator-devops/
├── src/main/java/com/spe/calculator/   # application, controller, service, model, exception handler
├── src/test/java/com/spe/calculator/   # JUnit 5 unit tests + MockMvc integration tests
├── nginx/default.conf                  # reverse proxy config
├── pom.xml
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── Jenkinsfile
└── docs/                               # report and screenshots
```
