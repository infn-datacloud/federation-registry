#!groovy
@Library('jenkins-libraries') _

pipeline {
    agent { label 'jenkinsworker00' }
    stages {
        stage('Run tests') {
            parallel {
                stage('Python 3.10') {
                    steps {
                        script {
                            pythonProject.formatCode('3.10', 'fed_reg')
                        }
                    }
                }
                stage('Python 3.11') {
                    steps {
                        script {
                            pythonProject.formatCode('3.11', 'fed_reg')
                        }
                    }
                }
            }
        }
    }
}
