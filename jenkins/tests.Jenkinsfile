#!groovy
@Library('jenkins-libraries') _

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
            pythonProject.testCode(
                pythonVersion: "${pythonVersion}",
                dockerArgs: "-e NEO4J_TEST_URL=bolt://neo4j:password@db:7687 --link ${c.id}:db",
                coveragercId: '.coveragerc',
                coverageDir: "${COVERAGE_DIR}",
                pytestArgs: '--resetdb'
                )
        }
    }
}

pipeline {
    agent { label 'jenkins-node-label-1' }

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
                stage('Run tests on python3.10') {
                    steps {
                        runTests('3.10')
                    }
                }
                stage('Run tests on python3.11') {
                    steps {
                        runTests('3.11')
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                sonar.analysis(
                    sonarToken: '${SONAR_TOKEN}',
                    sonarProject: "${SONAR_PROJECT}",
                    sonarOrganization: "${SONAR_ORGANIZATION}",
                    sonarHost: "${SONAR_HOST}",
                    coverageDir: "${COVERAGE_DIR}",
                    srcDir: 'fed_reg',
                    testsDir: 'tests',
                    pythonVersions: '3.10, 3.11'
                )
            }
        }
    }
}
