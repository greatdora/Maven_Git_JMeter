pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // 明确指定 main 分支
                git branch: 'main', url: 'https://github.com/greatdora/Maven_Git_JMeter.git'
            }
        }
        stage('Build') {
            steps {
                // 构建 Maven 项目
                sh 'mvn clean package'
            }
        }
        stage('Run JMeter Tests') {
            steps {
                // 假设你有 JMeter 脚本在 src/test/jmeter/sample_test.jmx
                sh '''
                    mkdir -p target/jmeter/results
                    jmeter -n -t src/test/jmeter/sample_test.jmx -l target/jmeter/results/result.csv
                '''
            }
        }
        stage('Publish JMeter Report') {
            steps {
                // 假设你安装了 Performance 插件
                perfReport errorFailedThreshold: 0, errorUnstableThreshold: 0, 
                    sourceDataFiles: 'target/jmeter/results/result.csv'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'target/jmeter/results/*.csv', fingerprint: true
        }
    }
}