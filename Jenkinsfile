pipeline {
    agent any
    triggers {
        cron('0 9,12,15,18 * * *') // 每天4次
    }
    options {
        // 自动清理构建历史
        buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '7'))
    }
    stages {
        stage('Build & Run JMeter') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'testCredential', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')
                ]) {
                    sh '''
                        export NOW=$(date +%Y%m%d_%H%M)
                        mvn clean verify -DUSERNAME=$USERNAME -DPASSWORD=$PASSWORD
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
                    
                    # 查找JMeter生成的结果文件
                    echo "查找JMeter结果文件..."
                    
                    # 方法1: 查找最新的CSV文件（JMeter插件生成的位置）
                    LATEST_CSV=$(find target -name "*.csv" -type f -path "*/jmeter/bin/*" | xargs ls -t | head -1)
                    if [ -n "$LATEST_CSV" ] && [ -f "$LATEST_CSV" ]; then
                        cp "$LATEST_CSV" compare_results/
                        echo "Found JMeter result file: $LATEST_CSV"
                    else
                        # 方法2: 查找其他可能的CSV文件
                        LATEST_CSV=$(find target -name "*.csv" -type f | xargs ls -t | head -1)
                        if [ -n "$LATEST_CSV" ] && [ -f "$LATEST_CSV" ]; then
                            cp "$LATEST_CSV" compare_results/
                            echo "Found CSV file: $LATEST_CSV"
                        else
                            echo "No CSV files found in target directory"
                            echo "Checking target directory structure:"
                            find target -type d -name "jmeter" 2>/dev/null || echo "No jmeter directories found"
                            find target -name "*.csv" 2>/dev/null || echo "No CSV files found"
                        fi
                    fi
                    
                    # 显示找到的文件
                    echo "Files in compare_results directory:"
                    ls -la compare_results/ || echo "compare_results directory is empty"
                    
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
                reportName: 'Performance Dashboard',
                reportTitles: 'JMeter Performance Dashboard',
                escapeUnderscores: false,
                includes: '**/*'
            ])
        }
        success {
            echo '构建成功！性能测试完成。'
            echo 'Dashboard已生成，可在Jenkins中查看Performance Dashboard报告。'
        }
        failure {
            echo '构建失败！请检查JMeter配置和测试环境。'
        }
    }
}