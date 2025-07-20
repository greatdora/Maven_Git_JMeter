pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // 明确指定 main 分支
                git branch: 'main', url: 'https://github.com/greatdora/Maven_Git_JMeter.git'
            }
        }
        stage('Build & Run JMeter') {
            steps {
                sh 'mvn clean verify'
            }
        }
        stage('Publish JMeter Report') {
            steps {
                perfReport errorFailedThreshold: 0, errorUnstableThreshold: 0, 
                    sourceDataFiles: 'target/jmeter/results/*.jtl'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'target/jmeter/results/*', fingerprint: true
        }
    }
}