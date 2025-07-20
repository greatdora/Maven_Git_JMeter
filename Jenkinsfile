    pipeline {
        agent any
        triggers {
            cron('H 2 * * *') // 每天凌晨2点自动运行
        }
        stages {
            stage('Checkout') {
                steps {
                    git url: 'https://github.com/greatdora/Maven_Git_JMeter.git'
                }
            }
            stage('Build & Run JMeter') {
                steps {
                    sh 'mvn clean verify'
                }
            }
        }
        post {
            always {
                perfReport sourceDataFiles: 'target/jmeter/results/*.csv'
            }
        }
    }