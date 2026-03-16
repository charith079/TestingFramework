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
                sh 'mkdir -p ${REPORTS_DIR} logs'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    python3 --version
                    pip3 --version
                    
                    # Create virtual environment if it doesn't exist
                    if [ ! -d "${VENV_DIR}" ]; then
                        echo "Creating Python virtual environment..."
                        python3 -m venv ${VENV_DIR}
                    fi
                    
                    # Activate virtual environment and install dependencies
                    source ${VENV_DIR}/bin/activate
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
                sh '''
                    # Stop any existing grid
                    docker-compose down || true
                    
                    # Start fresh grid
                    docker-compose up -d
                    
                    # Wait for grid to be ready
                    echo "Waiting for Selenium Grid to be ready..."
                    sleep 20
                    
                    # Check grid status
                    curl -f http://localhost:4444/status || exit 1
                    echo "Selenium Grid is ready!"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    def pytestCommand = buildPytestCommand()
                    
                    sh """
                        source ${VENV_DIR}/bin/activate
                        
                        # Set environment variables
                        export EXECUTION_MODE=${params.EXECUTION_MODE}
                        export BROWSER=${params.BROWSER}
                        export HEADLESS=${params.HEADLESS}
                        export BASE_URL=${BASE_URL}
                        export DEFAULT_WAIT=${DEFAULT_WAIT}
                        export GRID_URL=${GRID_URL}
                        export ADMIN_EMAIL=${ADMIN_EMAIL}
                        export ADMIN_PASSWORD=${ADMIN_PASSWORD}
                        export USER_EMAIL=${USER_EMAIL}
                        export USER_PASSWORD=${USER_PASSWORD}
                        
                        # Run tests
                        echo "Executing: ${pytestCommand}"
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
                sh '''
                    source ${VENV_DIR}/bin/activate
                    
                    # Generate Allure HTML report
                    if [ -d "reports/allure-results" ] && [ "$(ls -A reports/allure-results)" ]; then
                        echo "Generating Allure report..."
                        allure generate reports/allure-results -o reports/allure-html --clean
                        echo "Allure report generated successfully!"
                    else
                        echo "No Allure results found, skipping report generation"
                    fi
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
                        sh 'docker-compose down || true'
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
