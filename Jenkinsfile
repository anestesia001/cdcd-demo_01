def remote = [:]

pipeline {
    agent any
    parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: false)
        choice(name: 'ENV', choices: ['dev', 'prod'])
    }

    environment {
        REGISTRY = 'anestesia01/dos36'
        DOCKER_TOKEN = credentials('docker-token')
        IMAGE = "${env.REGISTRY}:demo-${BUILD_NUMBER}"
        DEV_HOST = "46.243.211.91"
        PROD_HOST = "127.0.0.1"
        PRJ_DIR = "/home/jenkins/cdcd-demo_01"
    }

    stages {
        stage('Choice host') {
            steps {
                script {
                    if (params.ENV == 'dev') {
                        env.HOST = env.DEV_HOST
                    } else if (params.ENV == 'prod') {
                        env.HOST = env.PROD_HOST
                    }
                }
            }
        }

        stage('Checkout repo') {
            steps {
                git(
                    branch: 'main',
                    url: 'git@github.com:anestesia001/cdcd-demo_01.git',
                    credentialsId: 'jenkins-key'
                )
            }
        }

        stage('Configure credentials') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'jenkins-key',
                        keyFileVariable: 'PRIVATE_KEY',
                        usernameVariable: 'USERNAME'
                    )
                ]) 
                {
                    script {
                        remote.name = env.HOST
                        remote.host = env.HOST
                        remote.user = ${USERNAME}
                        remote.identity = readFile(${PRIVATE_KEY})
                        remote.allowAnyHosts = true
                    }
                }
            }
        }

        stage('Build image') {
            steps {
                script {
                    sh """
                        docker build -t $IMAGE .
                    """
                }
            }
        }

        stage('Push image') {
            steps {
                script {
                    sh """
                        echo $DOCKER_TOKEN | docker login -u anestesia01 --password-stdin
                        docker push $IMAGE
                        docker logout
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        set -e
                        docker pull $IMAGE
                        cd ${env.PRJ_DIR}
                        sed -i "s|image: anestesia01.*|image: ${env.IMAGE}|" compose.yml
                        docker compose up -d
                    """
                }
            }
        }
    }

}