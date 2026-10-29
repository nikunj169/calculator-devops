"""Build the mini-project report PDF: make_report.py <shots_dir> <out.pdf>"""
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from PIL import Image as PILImage

shots, out = sys.argv[1], sys.argv[2]
W = A4[0] - 3.6 * cm

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.6, leading=12.6, spaceAfter=4)
small = ParagraphStyle("small", parent=body, fontSize=8.6, leading=11)
h1 = ParagraphStyle("h1", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, spaceBefore=8, spaceAfter=4,
                    textColor=colors.HexColor("#1a3d6d"))
title = ParagraphStyle("title", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=2)
sub = ParagraphStyle("sub", parent=body, alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor("#444444"))
cap = ParagraphStyle("cap", parent=small, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=small, fontSize=8.4, leading=10.4)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")


def img(name, width=W, max_h=None):
    w, h = PILImage.open(f"{shots}/{name}").size
    dw, dh = width, width * h / w
    if max_h and dh > max_h:
        dw, dh = dw * max_h / dh, max_h
    return Image(f"{shots}/{name}", dw, dh)


def table(rows, widths, header=True):
    data = [[Paragraph(c, cellb if (header and i == 0) or j == 0 else cell) for j, c in enumerate(r)]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(1.8 * cm, 1.1 * cm, "CSE 816 Software Production Engineering - Mini-Project Report")
    canvas.drawRightString(A4[0] - 1.8 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


s = []
s += [Paragraph("End-to-End CI/CD Pipeline for a Calculator REST API", title),
      Paragraph("CSE 816 Software Production Engineering - Mini-Project Report", sub),
      Paragraph("Nikunj Mahajan (IMT2023068)", sub), Spacer(1, 6)]

s.append(table([
    ["GitHub repository", '<link href="https://github.com/nikunj169/calculator-devops">'
                          'https://github.com/nikunj169/calculator-devops</link>'],
    ["Docker Hub image", '<link href="https://hub.docker.com/r/niki9937/calculator-devops">'
                         'https://hub.docker.com/r/niki9937/calculator-devops</link> (public, tags <i>:latest</i>, '
                         '<i>:&lt;build number&gt;</i>)'],
    ["Stack", "Java 21, Spring Boot 3.5 (Web + Actuator), Maven, JUnit 5 / MockMvc, Git/GitHub, Jenkins LTS "
              "(declarative pipeline), Docker (multi-stage), Docker Compose, Nginx"],
], [3.6 * cm, W - 3.6 * cm], header=False))

s.append(Paragraph("1. Overview", h1))
s.append(Paragraph(
    "The project is a small Calculator REST API wrapped in a fully automated delivery pipeline. A change merged "
    "into <b>main</b> on GitHub is detected by Jenkins, compiled, tested, packaged into a Docker image tagged with "
    "the Jenkins build number, pushed to Docker Hub and rolled out with Docker Compose behind an Nginx reverse "
    "proxy. The pipeline then checks the deployment's health, runs a smoke test, and emails the build result. No "
    "step needs manual intervention; build #1 was triggered by Poll SCM after the pull requests were merged and "
    "finished green in about four minutes.", body))

s.append(Paragraph("2. Pipeline architecture", h1))
s.append(img("architecture.png"))
s.append(Paragraph("Figure 1 - Flow from a Git push through the six Jenkins stages to Docker Hub and the Compose "
                   "deployment.", cap))

s.append(Paragraph("3. Application", h1))
s.append(Paragraph(
    "<b>Endpoints:</b> <font face='Courier'>GET /api/v1/{add,subtract,multiply,divide}?a=&amp;b=</font> return "
    "<font face='Courier'>{\"operation\":\"add\",\"a\":2,\"b\":3,\"result\":5}</font>; "
    "<font face='Courier'>/actuator/health</font> reports UP/DOWN. Arithmetic lives in a plain "
    "<i>CalculatorService</i>; the controller only validates input and wraps results. A "
    "<i>@RestControllerAdvice</i> maps missing parameters, non-numeric values, NaN/Infinity and division by zero "
    "to HTTP 400 with a structured body (timestamp, status, error, message, path). Whole-number results are "
    "rendered as integers so the JSON matches the specification (5, not 5.0).", body))
s.append(Paragraph(
    "<b>Tests (30, all passing):</b> parameterised JUnit 5 unit tests for every operation, including divide-by-zero "
    "and 0/0; a <i>@SpringBootTest</i> + MockMvc integration suite that calls each real endpoint, every error path "
    "and the Actuator health/info endpoints. <font face='Courier'>mvn test</font> writes Surefire JUnit XML, which "
    "Jenkins publishes.", body))

s.append(Paragraph("4. Pipeline stages", h1))
s.append(table([
    ["Stage", "What it does"],
    ["Trigger", "<font face='Courier'>githubPush()</font> for a GitHub webhook, and <font face='Courier'>pollSCM('H/2 * * * *')</font> "
                "as the working trigger, since this Jenkins runs on localhost and GitHub cannot reach it. "
                "<font face='Courier'>disableConcurrentBuilds</font> and a 30-minute timeout keep runs from overlapping."],
    ["Checkout", "<font face='Courier'>checkout scm</font> pulls the commit that triggered the build and logs it."],
    ["Build", "<font face='Courier'>mvn -B clean package -DskipTests</font> produces <i>target/calculator.jar</i>."],
    ["Test", "<font face='Courier'>mvn -B test</font>; a non-zero exit fails the stage and the build. "
             "<font face='Courier'>junit 'target/surefire-reports/*.xml'</font> runs in <i>post { always }</i>, so "
             "results are published even on failure."],
    ["Docker Build", "Builds the multi-stage image and tags it <i>niki9937/calculator-devops:&lt;BUILD_NUMBER&gt;</i> "
                     "and <i>:latest</i>."],
    ["Push", "Binds the Jenkins credential <i>dockerhub-credentials</i> via <font face='Courier'>credentials()</font> "
             "(masked in logs), logs in with <font face='Courier'>--password-stdin</font> using a throwaway "
             "<font face='Courier'>DOCKER_CONFIG</font>, pushes both tags, logs out and deletes the temporary config."],
    ["Deploy", "<font face='Courier'>docker compose up -d --remove-orphans --wait</font> with "
               "<font face='Courier'>IMAGE_TAG=BUILD_NUMBER</font>, then polls <i>/actuator/health</i> through "
               "Nginx and runs a smoke request; on failure it prints container logs and fails the build."],
    ["Post", "<font face='Courier'>emailext</font> sends an HTML success mail or a failure mail with the console log "
             "attached; dangling images are pruned."],
], [2.4 * cm, W - 2.4 * cm]))
s.append(Spacer(1, 4))
s.append(Paragraph(
    "<b>Idempotency:</b> the Compose project name is fixed (<i>calculator-devops</i>), so every run updates the same "
    "stack. <font face='Courier'>up -d</font> only recreates containers whose image or config changed, and a re-run "
    "of the same commit leaves the running deployment alone. <b>Secrets:</b> no credentials live in the repository; "
    "<i>.gitignore</i> excludes <i>target/</i>, IDE files, <i>.env</i> and key files.", body))

s.append(Paragraph("5. Containerisation and deployment", h1))
s.append(Paragraph(
    "<b>Dockerfile (multi-stage):</b> stage 1 (<i>maven:3.9-eclipse-temurin-21</i>) copies <i>pom.xml</i> first and "
    "runs <font face='Courier'>dependency:go-offline</font>, so the dependency layer stays cached until the POM "
    "changes, then copies <i>src/</i> and packages the JAR. Stage 2 (<i>eclipse-temurin:21-jre-alpine</i>, about 95 MB) "
    "copies only the JAR, creates and switches to a non-root <i>app</i> user, declares "
    "<font face='Courier'>EXPOSE 8080</font> and a <font face='Courier'>HEALTHCHECK</font>. A <i>.dockerignore</i> "
    "limits the build context to <i>pom.xml</i> and <i>src/</i>. "
    "<font face='Courier'>docker run -p 8085:8080 niki9937/calculator-devops</font> is all it takes to run it.", body))
s.append(Paragraph(
    "<b>docker-compose.yml:</b> two <i>calculator</i> replicas (<font face='Courier'>deploy.replicas: 2</font>) and an "
    "<i>nginx:1.27-alpine</i> reverse proxy published on port 8090, on a dedicated bridge network "
    "<i>calculator-net</i>. Both services have health checks (the API checks <i>/actuator/health</i> for "
    "<i>\"status\":\"UP\"</i>), <font face='Courier'>restart: unless-stopped</font>, and environment variables "
    "(<i>SERVER_PORT</i>, <i>JAVA_TOOL_OPTIONS</i>, <i>TZ</i>). Nginx starts only after the replicas report "
    "<i>service_healthy</i>. It resolves the service name through Docker DNS on every request, which spreads load "
    "across replicas (the <i>X-Upstream-Addr</i> header alternates) and follows new container IPs after a redeploy. "
    "One <font face='Courier'>docker compose up -d</font> starts the whole stack.", body))

s.append(Paragraph("6. Git workflow", h1))
s.append(Paragraph(
    "The application was built in small commits on <i>main</i> (skeleton, service + unit tests, controller + "
    "validation, integration tests). Containerisation, the Jenkinsfile and the README each went through their own "
    "feature branch and pull request (#1-#3), merged with merge commits so the branch history stays visible. "
    "PR #4 (deployed build number on <i>/actuator/info</i>) is the change for the live demo: merging it makes "
    "Jenkins build, push and deploy the next build automatically. Pushing this report to main already did "
    "the same thing: build #2 was triggered by Poll SCM and redeployed only the API replicas, leaving Nginx running.", body))

s.append(Paragraph("7. Challenges faced", h1))
s.append(table([
    ["Problem", "Resolution"],
    ["<i>eclipse-temurin:17-jre-alpine</i> has no arm64 image, so the build failed on Apple Silicon "
     "(<i>no match for platform in manifest</i>).",
     "Moved to Java 21 LTS, whose Alpine JRE is multi-arch and matches the JDK Jenkins runs on."],
    ["The Nginx container stayed <i>unhealthy</i>: <i>localhost</i> resolved to ::1 inside Alpine, but Nginx "
     "listens on IPv4 only.", "Health checks use 127.0.0.1 explicitly."],
    ["Nginx caches upstream IPs at startup, so after Jenkins recreated the API containers it would proxy to dead "
     "addresses.", "Used <font face='Courier'>resolver 127.0.0.11</font> with a variable in "
     "<font face='Courier'>proxy_pass</font>, which forces a DNS lookup per request."],
    ["The integration test class, at first named <i>*IT</i>, was silently skipped by Surefire.",
     "Renamed it to <i>CalculatorControllerIntegrationTest</i> so <font face='Courier'>mvn test</font> runs it."],
    ["Jenkins runs on localhost, so a GitHub webhook can't reach it.",
     "Kept <font face='Courier'>githubPush()</font> for a public Jenkins and added Poll SCM every 2 minutes."],
    ["<font face='Courier'>docker login/logout</font> in the pipeline would overwrite or wipe the host's Docker "
     "Desktop keychain login.", "The Push stage uses a temporary <font face='Courier'>DOCKER_CONFIG</font> with no "
     "credential helper and deletes it afterwards."],
    ["Jenkins started by launchd has no Homebrew PATH (<i>mvn</i>, <i>docker</i>).",
     "Prepended <i>/opt/homebrew/bin</i> in the pipeline's <font face='Courier'>environment</font>."],
    ["No SMTP account was configured in Jenkins.",
     "Pointed Email Extension at a local Mailpit SMTP server (localhost:1025) for the demo. Real delivery only "
     "needs Gmail SMTP (smtp.gmail.com:465, SSL, app password) configured in Jenkins; the Jenkinsfile stays the same."],
], [W * 0.5, W * 0.5]))
s.append(Paragraph(
    "<b>Known limitation:</b> the image is built on the Jenkins host, so it is arm64-only. A "
    "<font face='Courier'>docker buildx --platform linux/amd64,linux/arm64</font> build would make it multi-arch.",
    body))

# ---- Appendix: screenshots ----
s.append(PageBreak())
s.append(Paragraph("Appendix - Screenshots", h1))
for name, caption in [
    ("jenkins-console.png", "Figure 2 - Jenkins build #1 of <i>calculator-devops</i> (started by an SCM change): all "
                            "stages ran, 29 tests passed, both tags pushed, stack healthy, email sent, "
                            "<b>Finished: SUCCESS</b>."),
    ("email.png", "Figure 3 - Build-status email sent by Jenkins to the student's address, captured by the Mailpit SMTP "
                  "server."),
    ("docker-ps.png", "Figure 4 - <font face='Courier'>docker ps</font> after the pipeline deploy: two API replicas "
                      "running image tag <i>:1</i> and Nginx, all healthy."),
    ("api.png", "Figure 5 - Sample API responses through Nginx, including the 400 error bodies."),
    ("dockerhub.png", "Figure 6 - Public Docker Hub repository with the tags pushed by Jenkins."),
    ("gitlog.png", "Figure 7 - Commit history with feature branches and merged pull requests."),
]:
    s.append(KeepTogether([img(name, max_h=9.5 * cm), Paragraph(caption, cap)]))

doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.5 * cm,
                        bottomMargin=1.7 * cm, title="SPE Mini-Project Report - Calculator CI/CD",
                        author="Nikunj Mahajan")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(out)
