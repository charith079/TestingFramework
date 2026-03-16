pipeline {
    agent any

    parameters {
        choice(
            name: 'EXECUTION_MODE',
            choices: ['local', 'remote'],
            description: 'Test execution mode: local (single browser) or remote (Selenium Grid)'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox'],
            description: 'Browser to use for tests'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run tests in headless mode (no browser UI)'
        )
        choice(
            name: 'TEST_SCOPE',
            choices: ['all', 'smoke', 'regression', 'auth', 'access', 'projects', 'browser'],
            description: 'Test scope to execute'
        )
    }

    environment {
        // Python location - properly quoted for spaces
        PYTHON_HOME = 'C:\\Users\\charith reddy\\AppData\\Local\\Programs\\Python\\Python312'
        PYTHON = "\"${PYTHON_HOME}\\python.exe\""

        // Project directories
        VENV_DIR = 'venv'
        REPORTS_DIR = 'reports'

        // Test configuration
        BASE_URL = 'https://react-frontend-api-testing.vercel.app'
        DEFAULT_WAIT = '10'
        GRID_URL = 'http://localhost:4444/wd/hub'

        // Test credentials
        ADMIN_EMAIL = 'admin@example.com'
        ADMIN_PASSWORD = 'Admin@123'
        USER_EMAIL = 'user@example.com'
        USER_PASSWORD = 'User@123'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        timestamps()
    }

    stages {

        stage('Checkout from GitHub') {
            steps {
                echo 'Cloning repository...'
                git branch: 'master', url: 'https://github.com/charith079/TestingFramework.git'

                bat '''
                if not exist "reports" mkdir reports
                if not exist "logs" mkdir logs
                '''
            }
        }

        stage('Check Python') {
            steps {
                bat """
                echo Using Python from:
                "${PYTHON}"
                "${PYTHON}" --version
                """
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Creating virtual environment...'
                bat """
                if not exist "%VENV_DIR%" (
                    "${PYTHON}" -m venv %VENV_DIR%
                )

                call %VENV_DIR%\\Scripts\\activate.bat

                python -m pip install --upgrade pip
                pip install -r requirements.txt
                pip install allure-commandline
                """
            }
        }

        stage('Start Selenium Grid') {
            when {
                expression { params.EXECUTION_MODE == 'remote' }
            }
            steps {
                echo 'Starting Selenium Grid...'
                bat '''
                docker-compose down || exit /b 0
                docker-compose up -d

                echo Waiting for Selenium Grid...
                timeout /t 20 /nobreak

                curl -f http://localhost:4444/status || exit /b 1
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def pytestCommand = buildPytestCommand()

                    bat """
                    call %VENV_DIR%\\Scripts\\activate.bat

                    set EXECUTION_MODE=${params.EXECUTION_MODE}
                    set BROWSER=${params.BROWSER}
                    set HEADLESS=${params.HEADLESS}
                    set BASE_URL=${BASE_URL}
                    set DEFAULT_WAIT=${DEFAULT_WAIT}
                    set GRID_URL=${GRID_URL}

                    echo Running tests...
                    ${pytestCommand}
                    """
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: 'reports/**/*, logs/**/*', allowEmptyArchive: true
                    publishTestResults testResultsPattern: 'reports/junit.xml', allowEmptyResults: true
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                bat '''
                call venv\\Scripts\\activate.bat

                if exist "reports\\allure-results" (
                    allure generate reports\\allure-results -o reports\\allure-html --clean
                )
                '''
            }

            post {
                success {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/allure-html',
                        reportFiles: 'index.html',
                        reportName: 'Allure Test Report'
                    ])
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    if (params.EXECUTION_MODE == 'remote') {
                        bat 'docker-compose down || exit /b 0'
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished: ${currentBuild.result ?: 'SUCCESS'}"
        }

        success {
            echo 'All tests passed'
        }

        failure {
            echo 'Pipeline failed'
            archiveArtifacts artifacts: '**/*.log, **/*.png', allowEmptyArchive: true
        }
    }
}

def buildPytestCommand() {
    def command = "pytest"

    switch (params.TEST_SCOPE) {
        case 'smoke':
            command += " -m smoke"
            break
        case 'regression':
            command += " -m regression"
            break
        case 'auth':
            command += " -m auth"
            break
        case 'access':
            command += " -m access"
            break
        case 'projects':
            command += " -m projects"
            break
        case 'browser':
            command += " -m browser"
            break
    }

    if (params.EXECUTION_MODE == 'remote') {
        command += " -n 3 --dist=loadscope"
    }

    command += " --alluredir=reports/allure-results --junitxml=reports/junit.xml -v"

    return command
}