pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
        AWS_REGION = "ca-central-1"
        ECR_REGISTRY = "497535504649.dkr.ecr.ca-central-1.amazonaws.com"
        ECR_REPOSITORY = "cloud-native-devops-app"
    }

    stages {
        stage('Verify Node.js') {
            steps {
                sh 'node --version'
                sh 'npm --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('app') {
                    sh 'npm install'
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir('app') {
                    sh 'npm test'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cloud-native-devops-app:${BUILD_NUMBER} .'
            }
        }

        stage('Push Image to ECR') {
    
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

}

}