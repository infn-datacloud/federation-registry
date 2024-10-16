#!groovy
@Library('jenkins-libraries') _

pipeline {
    agent {
        node { label 'jenkinsworker00' }
    }

    environment {
        PROJECT_NAME = 'federation-registry'
        DOCKERFILE1 = './dockerfiles/Dockerfile.prod'
        DOCKERFILE2 = './dockerfiles/Dockerfile.k8s'

        DOCKER_HUB_CREDENTIALS_NAME = 'docker-hub-credentials'
        DOCKER_HUB_CREDENTIALS = credentials("${DOCKER_HUB_CREDENTIALS_NAME}")
        DOCKER_HUB_ORGANIZATION = 'indigopaas'
        DOCKER_HUB_URL = 'https://index.docker.io/v1/'
        DOCKER_HUB_HOST = 'docker.io'

        HARBOR_CREDENTIALS_NAME = 'harbor-paas-credentials'
        HARBOR_CREDENTIALS = credentials("${HARBOR_CREDENTIALS_NAME}")
        HARBOR_ORGANIZATION = 'datacloud-middleware'
        HARBOR_URL = 'https://harbor.cloud.infn.it'
        HARBOR_HOST = 'harbor.cloud.infn.it'
    }

    stages {
        stage('Create and push images') {
            parallel {
                stage('Image for single instance deployment with python 3.10 published on Harbor') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${HARBOR_ORGANIZATION}/${PROJECT_NAME}",
                                dockerfile: "${DOCKERFILE1}",
                                registryUrl: "${HARBOR_URL}",
                                registryCredentialsName: "${HARBOR_CREDENTIALS_NAME}",
                                registryUser: '${HARBOR_CREDENTIALS_USR}',
                                registryPassword: '${HARBOR_CREDENTIALS_PSW}',
                                registryHost: "${HARBOR_HOST}",
                                registryType: 'harbor2',
                                pythonVersion: '3.10'
                            )
                        }
                    }
                }
                stage('Image for single instance deployment with python 3.11 published on Harbor') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${HARBOR_ORGANIZATION}/${PROJECT_NAME}",
                                dockerfile: "${DOCKERFILE1}",
                                registryUrl: "${HARBOR_URL}",
                                registryCredentialsName: "${HARBOR_CREDENTIALS_NAME}",
                                registryUser: '${HARBOR_CREDENTIALS_USR}',
                                registryPassword: '${HARBOR_CREDENTIALS_PSW}',
                                registryHost: "${HARBOR_HOST}",
                                registryType: 'harbor2',
                                pythonVersion: '3.11'
                            )
                        }
                    }
                }
                stage('Image for single instance deployment with python 3.10 published on DockerHub') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}",
                                dockerfile: "${DOCKERFILE1}",
                                registryUrl: "${DOCKER_HUB_URL}",
                                registryCredentialsName: "${DOCKER_HUB_CREDENTIALS_NAME}",
                                registryUser: '${DOCKER_HUB_CREDENTIALS_USR}',
                                registryPassword: '${DOCKER_HUB_CREDENTIALS_PSW}',
                                registryHost: "${DOCKER_HUB_HOST}",
                                registryType: 'dockerhub',
                                pythonVersion: '3.10'
                            )
                        }
                    }
                }
                stage('Image for single instance deployment with python 3.11 published on DockerHub') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}",
                                dockerfile: "${DOCKERFILE1}",
                                registryUrl: "${DOCKER_HUB_URL}",
                                registryCredentialsName: "${DOCKER_HUB_CREDENTIALS_NAME}",
                                registryUser: '${DOCKER_HUB_CREDENTIALS_USR}',
                                registryPassword: '${DOCKER_HUB_CREDENTIALS_PSW}',
                                registryHost: "${DOCKER_HUB_HOST}",
                                registryType: 'dockerhub',
                                pythonVersion: '3.11'
                            )
                        }
                    }
                }
                stage('Image for kubernetes deployment with python 3.10 published on Harbor') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${HARBOR_ORGANIZATION}/${PROJECT_NAME}-k8s",
                                dockerfile: "${DOCKERFILE2}",
                                registryUrl: "${HARBOR_URL}",
                                registryCredentialsName: "${HARBOR_CREDENTIALS_NAME}",
                                registryUser: '${HARBOR_CREDENTIALS_USR}',
                                registryPassword: '${HARBOR_CREDENTIALS_PSW}',
                                registryHost: "${HARBOR_HOST}",
                                registryType: 'harbor2',
                                pythonVersion: '3.10',
                                customTags: ['k8s']
                            )
                        }
                    }
                }
                stage('Image for kubernetes deployment with python 3.11 published on Harbor') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${HARBOR_ORGANIZATION}/${PROJECT_NAME}-k8s",
                                dockerfile: "${DOCKERFILE2}",
                                registryUrl: "${HARBOR_URL}",
                                registryCredentialsName: "${HARBOR_CREDENTIALS_NAME}",
                                registryUser: '${HARBOR_CREDENTIALS_USR}',
                                registryPassword: '${HARBOR_CREDENTIALS_PSW}',
                                registryHost: "${HARBOR_HOST}",
                                registryType: 'harbor2',
                                pythonVersion: '3.11',
                                customTags: ['k8s']
                            )
                        }
                    }
                }
                stage('Image for kubernetes deployment with python 3.10 published on DockerHub') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}-k8s",
                                dockerfile: "${DOCKERFILE2}",
                                registryUrl: "${DOCKER_HUB_URL}",
                                registryCredentialsName: "${DOCKER_HUB_CREDENTIALS_NAME}",
                                registryUser: '${DOCKER_HUB_CREDENTIALS_USR}',
                                registryPassword: '${DOCKER_HUB_CREDENTIALS_PSW}',
                                registryHost: "${DOCKER_HUB_HOST}",
                                registryType: 'dockerhub',
                                pythonVersion: '3.10',
                                customTags: ['k8s']
                            )
                        }
                    }
                }
                stage('Image for kubernetes deployment with python 3.11 published on DockerHub') {
                    steps {
                        script {
                            dockerRepository.buildAndPushImage(
                                imageName: "${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}-k8s",
                                dockerfile: "${DOCKERFILE2}",
                                registryUrl: "${DOCKER_HUB_URL}",
                                registryCredentialsName: "${DOCKER_HUB_CREDENTIALS_NAME}",
                                registryUser: '${DOCKER_HUB_CREDENTIALS_USR}',
                                registryPassword: '${DOCKER_HUB_CREDENTIALS_PSW}',
                                registryHost: "${DOCKER_HUB_HOST}",
                                registryType: 'dockerhub',
                                pythonVersion: '3.11',
                                customTags: ['k8s']
                            )
                        }
                    }
                }
            }
        }
   }
}
