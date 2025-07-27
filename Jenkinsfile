pipeline {
    agent any
    triggers {
        cron('0 9,12,15,18 * * *') // 每天4次
    }
    stages {
        stage('Build & Run JMeter') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'testCredential', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')
                ]) {
                    sh '''
                        export NOW=$(date +%Y%m%d_%H%M)
                        mvn clean verify -Djmeter.result.file.name=sample_test_$NOW -DUSERNAME=$USERNAME -DPASSWORD=$PASSWORD
                    '''
                }
            }
        }
        stage('Analyze Results & Generate Dashboard') {
            steps {
                sh '''
                    export NOW=$(date +%Y%m%d_%H%M)
                    export TODAY=$(date +%Y%m%d)
                    mkdir -p compare_results
                    
                    # 尝试多种可能的文件名格式
                    if [ -f "target/jmeter/results/sample_test_$NOW.csv" ]; then
                        cp target/jmeter/results/sample_test_$NOW.csv compare_results/
                        echo "Found file: sample_test_$NOW.csv"
                    elif [ -f "target/jmeter/results/$TODAY-sample_test.csv" ]; then
                        cp target/jmeter/results/$TODAY-sample_test.csv compare_results/
                        echo "Found file: $TODAY-sample_test.csv"
                    else
                        # 查找最新的CSV文件
                        LATEST_CSV=$(find target/jmeter/results -name "*.csv" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
                        if [ -n "$LATEST_CSV" ]; then
                            cp "$LATEST_CSV" compare_results/
                            echo "Found latest CSV file: $LATEST_CSV"
                        else
                            echo "No CSV files found in target/jmeter/results/"
                            ls -la target/jmeter/results/ || echo "No results directory found"
                            find target -name "*.csv" -o -name "*.jtl" || echo "No result files found"
                        fi
                    fi
                    
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