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
                    sourceDataFiles: 'target/jmeter/results/*.csv'
            }
        }
        stage('Compare TG1 TG2 Performance') {
            steps {
                sh '''
                    mkdir -p compare_results
                    cp target/jmeter/results/*.csv compare_results/
                    docker run --rm -v $PWD/compare_results:/data -v $PWD/compare_tg.py:/data/compare_tg.py python:3.11 \
                        bash -c "pip install pandas matplotlib && python /data/compare_tg.py"
                '''
                archiveArtifacts artifacts: 'compare_results/tg_compare.png', fingerprint: true
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'target/jmeter/results/*', fingerprint: true
        }
    }
}