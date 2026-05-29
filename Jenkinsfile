@Library('shared-libraries') _

pipeline{

    agent none;

    environment{
        JAVA_HOME_DIR="/home/builder/java/jdk-17.0.2"
        GRADLE_DIR   =".gradle"
        PYTHON313_BIN="/home/builder/python/Python-3.13.7/bin"
    }

    options {
        checkoutToSubdirectory 'marklogic-python-client'
        buildDiscarder logRotator(artifactDaysToKeepStr: '7', artifactNumToKeepStr: '', daysToKeepStr: '30', numToKeepStr: '5')
    }

    stages{
        stage('tests'){
            agent {label 'devExpLinuxPool'}
            steps{
              cleanupDocker()
              sh label:'mlsetup', script: '''#!/bin/bash
                echo "Removing any running MarkLogic server and clean up MarkLogic data directory"
                sudo /usr/local/sbin/mladmin remove
                docker-compose down -v || true
                sudo /usr/local/sbin/mladmin cleandata
                cd marklogic-python-client/test-app
                MARKLOGIC_LOGS_VOLUME=/tmp docker-compose up -d --build
              '''
              sh label:'deploy project', script: '''#!/bin/bash
                export JAVA_HOME=$JAVA_HOME_DIR
                export GRADLE_USER_HOME=$WORKSPACE/$GRADLE_DIR
                export PATH=$GRADLE_USER_HOME:$JAVA_HOME/bin:$PATH
                cd marklogic-python-client/test-app
                ./gradlew -i mlWaitTillReady
                ./gradlew -i mlDeploy -PmlPassword=admin
              '''
              // 'set -e' causes the script to fail if any command fails.
              sh label:'Run tests', script: '''#!/bin/bash
                set -e
                cd marklogic-python-client
                export PATH="${PYTHON313_BIN}:${PATH}"
                python3.13 --version
                python3.13 -m venv .venv
                source .venv/bin/activate
                python --version
                python -m pip install poetry
                poetry install
                pytest --junitxml=TestReport.xml || true
              '''
              junit 'marklogic-python-client/TestReport.xml'
            }
            post{
              always{
                updateWorkspacePermissions()
                sh label:'mlcleanup', script: '''#!/bin/bash
                  cd marklogic-python-client/test-app
                  docker-compose down -v || true
                '''
                cleanupDocker()
              }
            }
        }
    }
}
