pipeline {
    agent any
    triggers {
        cron('0 9,12,15,18 * * *') // 每天4次
    }
    stages {
        stage('Build & Run JMeter') {
            steps {
                withCredentials([
                    string(credentialsId: 'JMETER_USERNAME', variable: 'USERNAME'),
                    string(credentialsId: 'JMETER_PASSWORD', variable: 'PASSWORD')
                ]) {
                    sh '''
                        export NOW=$(date +%Y%m%d_%H%M)
                        mvn clean verify -Djmeter.result.file.name=sample_test_$NOW -JUSERNAME=$USERNAME -JPASSWORD=$PASSWORD
                    '''
                }
            }
        }
        stage('Analyze Results & Generate Dashboard') {
            steps {
                sh '''
                    export NOW=$(date +%Y%m%d_%H%M)
                    mkdir -p compare_results
                    cp target/jmeter/results/sample_test_$NOW.csv compare_results/
                    pip3 install --user pandas matplotlib jinja2 -i https://pypi.tuna.tsinghua.edu.cn/simple
                    python3 compare_tg.py
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