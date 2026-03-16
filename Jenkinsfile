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
                echo 'Cloning repository from GitHub...'
                git branch: 'master', url: 'https://github.com/charith079/TestingFramework.git'
                
                // Create necessary directories
                bat 'mkdir %REPORTS_DIR% 2>nul & mkdir logs 2>nul'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python environment...'
                bat '''
                    python --version
                    pip --version
                    
                    REM Create virtual environment if it doesn't exist
                    if not exist "%VENV_DIR%" (
                        echo Creating Python virtual environment...
                        python -m venv %VENV_DIR%
                    )
                    
                    REM Activate virtual environment and install dependencies
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install allure-commandline
                '''
            }
        }
        
        stage('Start Selenium Grid') {
            when {
                expression { params.EXECUTION_MODE == 'remote' }
            }
            steps {
                echo 'Starting Selenium Grid...'
                bat '''
                    REM Stop any existing grid
                    docker-compose down || exit /b 0
                    
                    REM Start fresh grid
                    docker-compose up -d
                    
                    REM Wait for grid to be ready
                    echo Waiting for Selenium Grid to be ready...
                    timeout /t 20 /nobreak
                    
                    REM Check grid status
                    curl -f http://localhost:4444/status || exit /b 1
                    echo Selenium Grid is ready!
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    def pytestCommand = buildPytestCommand()
                    
                    bat """
                        call %VENV_DIR%\\Scripts\\activate.bat
                        
                        REM Set environment variables
                        set EXECUTION_MODE=${params.EXECUTION_MODE}
                        set BROWSER=${params.BROWSER}
                        set HEADLESS=${params.HEADLESS}
                        set BASE_URL=${BASE_URL}
                        set DEFAULT_WAIT=${DEFAULT_WAIT}
                        set GRID_URL=${GRID_URL}
                        set ADMIN_EMAIL=${ADMIN_EMAIL}
                        set ADMIN_PASSWORD=${ADMIN_PASSWORD}
                        set USER_EMAIL=${USER_EMAIL}
                        set USER_PASSWORD=${USER_PASSWORD}
                        
                        REM Run tests
                        echo Executing: ${pytestCommand}
                        ${pytestCommand}
                    """
                }
            }
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: 'reports/**/*, logs/**/*', allowEmptyArchive: true
                    publishTestResults testResultsPattern: 'reports/junit.xml', allowEmptyResults: true
                }
            }
        }
        
        stage('Generate Allure Report') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    
                    REM Generate Allure HTML report
                    if exist "reports\\allure-results" (
                        dir "reports\\allure-results" /b | findstr /r "." > nul
                        if not errorlevel 1 (
                            echo Generating Allure report...
                            allure generate reports\\allure-results -o reports\\allure-html --clean
                            echo Allure report generated successfully!
                        ) else (
                            echo No Allure results found, skipping report generation
                        )
                    ) else (
                        echo Allure results directory not found, skipping report generation
                    )
                '''
            }
            post {
                success {
                    // Publish Allure report
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/allure-html',
                        reportFiles: 'index.html',
                        reportName: 'Allure Test Report',
                        reportTitles: 'UI Automation Test Results'
                    ])
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    if (params.EXECUTION_MODE == 'remote') {
                        echo 'Stopping Selenium Grid...'
                        bat 'docker-compose down || exit /b 0'
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline completed with status: ${currentBuild.result ?: 'SUCCESS'}"
        }
        
        success {
            echo '✅ All tests passed successfully!'
            echo '📊 Allure Report available in build artifacts'
        }
        
        failure {
            echo '❌ Pipeline failed! Check the logs above for details.'
            archiveArtifacts artifacts: '**/*.log, **/*.png, **/*.jpg', allowEmptyArchive: true
        }
        
        unstable {
            echo '⚠️ Tests completed with failures. Review the test report.'
        }
    }
}

// Helper function to build pytest command based on parameters
def buildPytestCommand() {
    def command = "pytest"
    
    // Add test scope
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
        case 'all':
        default:
            // Run all tests
            break
    }
    
    // Add parallel execution for remote mode
    if (params.EXECUTION_MODE == 'remote') {
        command += " -n 3 --dist=loadscope"
    }
    
    // Add output options
    command += " --alluredir=reports/allure-results --junitxml=reports/junit.xml -v"
    
    return command
}
