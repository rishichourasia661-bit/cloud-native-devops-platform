pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
        AWS_REGION = "ca-central-1"
        ECR_REGISTRY = "497535504649.dkr.ecr.ca-central-1.amazonaws.com"
        ECR_REPOSITORY = "cloud-native-devops-app"
    }

    stages {

        stage('Check Commit') {
            steps {
                script {
                    env.COMMIT_MESSAGE = sh(
                        script: "git log -1 --pretty=%B",
                        returnStdout: true
                    ).trim()

                    env.SKIP_CI = env.COMMIT_MESSAGE.startsWith(
                        "Update staging image tag"
                    ).toString()

                    echo "Commit: ${env.COMMIT_MESSAGE}"
                    echo "Skip CI: ${env.SKIP_CI}"
                }
            }
        }

        stage('Verify Node.js') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                sh 'node --version'
                sh 'npm --version'
            }
        }

        stage('Install Dependencies') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                dir('app') {
                    sh 'npm install'
                }
            }
        }

        stage('Run Tests') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                dir('app') {
                    sh 'npm test'
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                sh 'docker build -t cloud-native-devops-app:${BUILD_NUMBER} .'
            }
        }

        stage('Push Image to ECR') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-ecr-credentials'
                ]]) {
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login \
                        --username AWS \
                        --password-stdin ${ECR_REGISTRY}

                        docker tag cloud-native-devops-app:${BUILD_NUMBER} \
                        ${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}

                        docker push \
                        ${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Update GitOps Image Tag') {
            when {
                expression { env.SKIP_CI != 'true' }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-gitops',
                    usernameVariable: 'GIT_USERNAME',
                    passwordVariable: 'GIT_PASSWORD'
                )]) {
                    sh '''
                        sed -i '' "s/tag: \".*\"/tag: \\"${BUILD_NUMBER}\\"/" \
                        helm/cloud-native-devops-app/values.yaml

                        git config user.name "Jenkins"
                        git config user.email "jenkins@localhost"

                        git add helm/cloud-native-devops-app/values.yaml

                        git commit -m "Update staging image tag to ${BUILD_NUMBER}"

                        git push \
                        https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/rishichourasia661-bit/cloud-native-devops-platform.git \
                        HEAD:main
                    '''
                }
            }
        }
    }
}
