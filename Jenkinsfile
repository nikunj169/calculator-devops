// Declarative CI/CD pipeline for the Calculator REST API.
// Checkout -> Build -> Test -> Docker Build -> Push -> Deploy (Docker Compose)
pipeline {
    agent any

    triggers {
        // GitHub webhook (needs a publicly reachable Jenkins URL) ...
        githubPush()
        // ... with Poll SCM as a fallback for a Jenkins running on localhost
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        // Homebrew-installed mvn/docker on the macOS Jenkins host
        PATH = "/opt/homebrew/bin:/usr/local/bin:${env.PATH}"
        DOCKER_IMAGE = 'niki9937/calculator-devops'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        PROXY_PORT = '8090'
        APP_URL = "http://localhost:${PROXY_PORT}"
        NOTIFY_EMAIL = 'nikunjmahajan9937@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty=format:"%h %an: %s"'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn -B clean package -DskipTests'
            }
        }

        stage('Test') {
            steps {
                sh 'mvn -B test'
            }
            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml', allowEmptyResults: false
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t "$DOCKER_IMAGE:$IMAGE_TAG" -t "$DOCKER_IMAGE:latest" .'
            }
        }

        stage('Push') {
            environment {
                DOCKERHUB = credentials('dockerhub-credentials')
            }
            steps {
                // Log in with a throwaway client config so the Jenkins credential never
                // touches the host's keychain or default Docker login.
                sh '''
                    export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
                    export DOCKER_CONFIG="$WORKSPACE/.docker-push"
                    rm -rf "$DOCKER_CONFIG" && mkdir -p "$DOCKER_CONFIG"
                    echo '{}' > "$DOCKER_CONFIG/config.json"
                    PATH=/opt/homebrew/bin:/usr/bin:/bin
                    echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
                    docker push "$DOCKER_IMAGE:$IMAGE_TAG"
                    docker push "$DOCKER_IMAGE:latest"
                    docker logout
                    rm -rf "$DOCKER_CONFIG"
                '''
            }
        }

        stage('Deploy') {
            steps {
                // 'up -d' only recreates containers whose image/config changed, so
                // re-running the pipeline is safe against a live deployment.
                sh 'docker compose up -d --remove-orphans --wait --wait-timeout 120'
                sh 'docker compose ps'
                sh '''
                    for i in $(seq 1 20); do
                        if curl -fsS "$APP_URL/actuator/health" | grep -q '"status":"UP"'; then
                            echo "Health check passed"
                            curl -fsS "$APP_URL/api/v1/add?a=2&b=3"; echo
                            exit 0
                        fi
                        sleep 3
                    done
                    echo "Deployment did not become healthy" >&2
                    docker compose logs --tail 50
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                mimeType: 'text/html',
                body: """<p>Build <b>#${env.BUILD_NUMBER}</b> of <b>${env.JOB_NAME}</b> succeeded.</p>
                         <ul>
                           <li>Commit: ${env.GIT_COMMIT}</li>
                           <li>Image: ${env.DOCKER_IMAGE}:${env.IMAGE_TAG}</li>
                           <li>Deployed at: ${env.APP_URL}</li>
                         </ul>
                         <p><a href="${env.BUILD_URL}">Open build in Jenkins</a></p>"""
            )
        }
        failure {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                mimeType: 'text/html',
                attachLog: true,
                body: """<p>Build <b>#${env.BUILD_NUMBER}</b> of <b>${env.JOB_NAME}</b> failed.</p>
                         <p>Commit: ${env.GIT_COMMIT}</p>
                         <p><a href="${env.BUILD_URL}console">Console output</a> (log attached)</p>"""
            )
        }
        always {
            // Drop dangling layers left behind by rebuilt tags
            sh 'docker image prune -f || true'
        }
    }
}
