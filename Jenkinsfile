pipeline {
    agent any
    
    parameters {
        choice(
            name: 'EXECUTION_MODE',
            choices: ['local', 'remote'],
            description: 'Test execution mode'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox'],
            description: 'Browser to use for tests'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run tests in headless mode'
        )
        choice(
            name: 'TEST_SCOPE',
            choices: ['all', 'smoke', 'regression', 'auth', 'access', 'projects', 'browser'],
            description: 'Test scope to execute'
        )
        booleanParam(
            name: 'GENERATE_ALLURE_REPORT',
            defaultValue: true,
            description: 'Generate Allure HTML report'
        )
        booleanParam(
            name: 'CLEAN_WORKSPACE',
            defaultValue: true,
            description: 'Clean workspace before build'
        )
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = 'venv'
        REQUIREMENTS_FILE = 'requirements.txt'
        REPORTS_DIR = 'reports'
        ALLURE_RESULTS_DIR = 'reports/allure-results'
        ALLURE_HTML_DIR = 'reports/allure-html'
        JUNIT_XML = 'reports/junit.xml'
        
        // Test configuration
        BASE_URL = 'https://react-frontend-api-testing.vercel.app'
        DEFAULT_WAIT = '10'
        
        // Selenium Grid configuration
        GRID_URL = 'http://localhost:4444/wd/hub'
        
        // Test credentials (should be secured in real Jenkins)
        ADMIN_EMAIL = 'admin@example.com'
        ADMIN_PASSWORD = 'Admin@123'
        USER_EMAIL = 'user@example.com'
        USER_PASSWORD = 'User@123'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Preparation') {
            steps {
                script {
                    if (params.CLEAN_WORKSPACE) {
                        cleanWs()
                    }
                }
                
                echo "Starting UI Automation Pipeline"
                echo "Execution Mode: ${params.EXECUTION_MODE}"
                echo "Browser: ${params.BROWSER}"
                echo "Headless: ${params.HEADLESS}"
                echo "Test Scope: ${params.TEST_SCOPE}"
                
                // Git checkout (assuming Jenkins is configured with git repo)
                checkout scm
                
                // Create necessary directories
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    mkdir -p ${ALLURE_RESULTS_DIR}
                    mkdir -p logs
                '''
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    // Check if Python is available
                    sh '''
                        python --version
                        pip --version
                    '''
                    
                    // Create virtual environment if it doesn't exist
                    sh '''
                        if [ ! -d "${VENV_DIR}" ]; then
                            echo "Creating Python virtual environment..."
                            python -m venv ${VENV_DIR}
                        fi
                        
                        # Activate virtual environment
                        source ${VENV_DIR}/bin/activate
                        
                        # Upgrade pip
                        pip install --upgrade pip
                        
                        # Install requirements
                        echo "Installing Python dependencies..."
                        pip install -r ${REQUIREMENTS_FILE}
                        
                        # Install additional tools for CI
                        pip install allure-commandline
                    '''
                }
            }
        }
        
        stage('Start Selenium Grid') {
            when {
                expression { params.EXECUTION_MODE == 'remote' }
            }
            steps {
                script {
                    try {
                        echo "Starting Selenium Grid..."
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
                    } catch (Exception e) {
                        error "Failed to start Selenium Grid: ${e.getMessage()}"
                    }
                }
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
                    // Archive test results and logs
                    archiveArtifacts artifacts: 'reports/**/*, logs/**/*', allowEmptyArchive: true
                    
                    // Publish JUnit results
                    publishTestResults testResultsPattern: 'reports/junit.xml', allowEmptyResults: true
                }
            }
        }
        
        stage('Generate Allure Report') {
            when {
                expression { params.GENERATE_ALLURE_REPORT }
            }
            steps {
                script {
                    sh """
                        source ${VENV_DIR}/bin/activate
                        
                        # Generate Allure HTML report
                        if [ -d "${ALLURE_RESULTS_DIR}" ] && [ "\$(ls -A ${ALLURE_RESULTS_DIR})" ]; then
                            echo "Generating Allure report..."
                            allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_HTML_DIR} --clean
                            echo "Allure report generated successfully!"
                        else
                            echo "No Allure results found, skipping report generation"
                        fi
                    """
                }
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
                        echo "Stopping Selenium Grid..."
                        sh 'docker-compose down || true'
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline completed with status: ${currentBuild.result ?: 'SUCCESS'}"
            
            // Send notifications (customize based on your needs)
            script {
                if (currentBuild.result == 'FAILURE') {
                    echo "NOTIFICATION: Build failed! Check logs for details."
                    // Add email/Slack notification here if needed
                } else if (currentBuild.result == 'UNSTABLE') {
                    echo "NOTIFICATION: Build completed with test failures."
                } else {
                    echo "NOTIFICATION: Build completed successfully!"
                }
            }
        }
        
        success {
            echo "✅ All tests passed successfully!"
            
            // Display summary
            script {
                if (params.GENERATE_ALLURE_REPORT && fileExists('reports/allure-html/index.html')) {
                    echo "📊 Allure Report: ${BUILD_URL}Allure_Report/"
                }
            }
        }
        
        failure {
            echo "❌ Pipeline failed! Check the logs above for details."
            
            // Archive additional debugging information
            archiveArtifacts artifacts: '**/*.log, **/*.png, **/*.jpg', allowEmptyArchive: true
        }
        
        unstable {
            echo "⚠️ Tests completed with failures. Review the test report."
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
    
    // Add output options (already in pytest.ini but ensuring consistency)
    command += " --alluredir=${ALLURE_RESULTS_DIR} --junitxml=${JUNIT_XML} -v"
    
    return command
}
