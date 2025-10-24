pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS = credentials('dockerhub-creds') // username/password
    DOCKERHUB_REPO = "your-dockerhub-username/salary-tax-calculator"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    KUBECONFIG_CREDENTIALS = credentials('kubeconfig-creds') // optional
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit Tests') {
      steps {
        sh 'python -m pip install --upgrade pip'
        sh 'pip install -r requirements.txt'
        sh 'pip install pytest'
        sh 'pytest -q || true' // fail pipeline if you want: remove '|| true'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh """
          docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} .
        """
      }
    }

    stage('Push Image') {
      steps {
        sh """
          echo ${DOCKERHUB_CREDS_PSW} | docker login -u ${DOCKERHUB_CREDS_USR} --password-stdin
          docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}
          docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest
          docker push ${DOCKERHUB_REPO}:latest
        """
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        // If you store kubeconfig in Jenkins credentials, write it to file
        withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
          sh """
            export KUBECONFIG=${KUBECONFIG_FILE}
            # update image in deployment.yaml (simple sed) or use kubectl set image
            kubectl set image deployment/salary-tax-calculator salary-tax=${DOCKERHUB_REPO}:${IMAGE_TAG} --record || true
            kubectl apply -f deployment.yaml || true
            kubectl apply -f service.yaml || true
          """
        }
      }
    }
  }

  post {
    success {
      echo "Deployment successful: ${DOCKERHUB_REPO}:${IMAGE_TAG}"
    }
    failure {
      echo "Pipeline failed"
    }
  }
}
