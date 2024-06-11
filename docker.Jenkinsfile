def pushImage(image_name, registry_url, registry_credentials) {
    // Login to target registry, retrieve docker image and push it to the registry
    script {
        sh("docker tag ${PROJECT_NAME} ${image_name}")
        docker.withRegistry("${registry_url}", "${registry_credentials}") {
            if ("${BRANCH_NAME}" == "main") {           
                docker.image("${image_name}").push()
            }
            docker.image("${image_name}").push("${BRANCH_NAME}")
            docker.image("${image_name}").push("${COMMIT_SHA}")
        }
    }
}

pipeline {

    agent {
        node { label "jenkinsworker00" }
    }

    environment {
        PROJECT_NAME = "federation-registry"
        
        DOCKER_HUB_CREDENTIALS = "docker-hub-credentials"
        DOCKER_HUB_ORGANIZATION = "indigopaas"
        DOCKER_HUB_URL = "https://index.docker.io/v1/"
        
        HARBOR_CREDENTIALS = "harbor-paas-credentials"
        HARBOR_ORGANIZATION = "datacloud-middleware"
        HARBOR_URL = "https://harbor.cloud.infn.it"
        
        BRANCH_NAME = "${env.BRANCH_NAME != null ? env.BRANCH_NAME : 'main'}"
        COMMIT_SHA = sh(returnStdout: true, script: "git rev-parse --short=10 HEAD").trim()
    }

    stages {
        stage("Build and push docker images") {
            parallel {
                stage("Image for single instance deployment") {
                    stages {
                        stage("Build") {
                            steps {
                                script {
                                    dockerImage = docker.build("${PROJECT_NAME}", "-f ./dockerfiles/Dockerfile.prod")
                                }
                            }
                        }
                        stage("Push to registries") {
                            parallel {
                                stage("Harbor") {
                                    steps {
                                        pushImage("${HARBOR_ORGANIZATION}/${PROJECT_NAME}", "${HARBOR_URL}", "${HARBOR_CREDENTIALS}")
                                    }
                                }
                                stage("DockerHub") {
                                    steps {
                                        pushImage("${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}", "${DOCKER_HUB_URL}", "${DOCKER_HUB_CREDENTIALS}")
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Image for single instance deployment") {
                    stages {
                        stage("Build") {
                            steps {
                                script {
                                    docker.build("${PROJECT_NAME}-k8s", "-f ./dockerfiles/Dockerfile.k8s")
                                }
                            }
                        }
                        stage("Push to registries") {
                            parallel {
                                stage("Harbor") {
                                    steps {
                                        pushImage("${HARBOR_ORGANIZATION}/${PROJECT_NAME}-k8s", "${HARBOR_URL}", "${HARBOR_CREDENTIALS}")
                                    }
                                }
                                stage("DockerHub") {
                                    steps {
                                        pushImage("${DOCKER_HUB_ORGANIZATION}/${PROJECT_NAME}-k8s", "${DOCKER_HUB_URL}", "${DOCKER_HUB_CREDENTIALS}")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Remove docker image") {
            steps{
                script {
                    sh("docker rmi ${PROJECT_NAME}")
                    sh("docker rmi ${PROJECT_NAME}-k8s")
                }
            }
        }
        
    }
}
