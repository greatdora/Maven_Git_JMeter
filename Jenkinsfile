pipeline {
    agent any
    triggers {
        cron('0 9,12,15,18 * * *') // 每天4次
    }
    stages {
        stage('Build & Run JMeter') {
            steps {
                sh 'mvn clean verify'
            }
        }
        stage('Analyze Results & Generate Dashboard') {
            steps {
                sh '''
                    mkdir -p compare_results
                    cp target/jmeter/results/*.csv compare_results/
                    docker run --rm \
                      -v $WORKSPACE:/data \
                      python:3.11 \
                      bash -c "pip install pandas matplotlib jinja2 && python /data/compare_tg.py"
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'compare_results/*', fingerprint: true
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'compare_results',
                reportFiles: 'dashboard.html',
                reportName: 'Performance Dashboard'
            ])
        }
    }
}