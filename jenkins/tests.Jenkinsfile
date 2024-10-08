void runTests(String pythonVersion) {
    // Run in backgound a dockerized neo4j DB instance.
    // Install dependencies for the specified python version.
    // Run tests.
    script {
        docker
        .image("${NEO4J_IMAGE}")
        .withRun('-e NEO4J_AUTH=none -e NEO4J_PLUGINS=apoc') { c ->
            docker
            .image("${NEO4J_IMAGE}")
            .inside("--link ${c.id}:db") {
                sh 'while ! wget http://db:7474; do sleep 1; done' // Wait DB is up and running
            }
            docker
            .image("ghcr.io/withlogicco/poetry:1.8.3-python-${pythonVersion}-slim")
            .inside("""-e POETRY_VIRTUALENVS_PATH=${WORKSPACE}/.venv-${pythonVersion} \
                -e NEO4J_TEST_URL=bolt://neo4j:password@db:7687 \
                -u root:root \
                --link ${c.id}:db""") {
                sh "mkdir -p ${WORKSPACE}/.venv-${pythonVersion}"
                sh 'poetry install'
                configFileProvider([configFile(fileId:  '.coveragerc', variable: 'COVERAGERC')]) {
                    sh """poetry run pytest \
                        --resetdb \
                        --cov \
                        --cov-config=${COVERAGERC} \
                        --cov-report=xml:${COVERAGE_DIR}/coverage-${pythonVersion}.xml \
                        --cov-report=html:${COVERAGE_DIR}/htmlcov-${pythonVersion}"""
                }
        }
    }
}
}

pipeline {
    agent { label 'jenkinsworker00' }

    environment {
        NEO4J_IMAGE = 'neo4j:5.18'
        COVERAGE_DIR = 'coverage-reports'
        SONAR_HOST = 'https://sonarcloud.io'
        SONAR_ORGANIZATION = 'infn-datacloud'
        SONAR_PROJECT = 'federation-registry'
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Run tests on multiple python versions') {
            parallel {
                stage('Run on tests on python3.10') {
                    steps {
                        runTests('3.10')
                    }
                }
                stage('Run on tests on python3.11') {
                    steps {
                        runTests('3.11')
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: "${COVERAGE_DIR}/**/*", fingerprint: true
            sh '''docker run --rm \
                -e SONAR_HOST_URL=${SONAR_HOST} \
                -e SONAR_TOKEN=${SONAR_TOKEN} \
                -v ${WORKSPACE}:/usr/src \
                sonarsource/sonar-scanner-cli \
                -D sonar.projectKey=${SONAR_ORGANIZATION}_${SONAR_PROJECT} \
                -D sonar.organization=${SONAR_ORGANIZATION} \
                -D sonar.sources=fed_reg \
                -D sonar.tests=tests \
                -D sonar.python.version='3.10, 3.11'
                '''
        }
    }
}
