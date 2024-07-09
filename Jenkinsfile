@Library('shared-libraries') _
pipeline{
    agent none;
    environment{
        JAVA_HOME_DIR="/home/builder/java/jdk-11.0.2"
        GRADLE_DIR   =".gradle"
    }
    options {
        checkoutToSubdirectory 'marklogic-python-client'
        buildDiscarder logRotator(artifactDaysToKeepStr: '7', artifactNumToKeepStr: '', daysToKeepStr: '30', numToKeepStr: '')
    }
    stages{
        stage('tests'){
            agent {label 'devExpLinuxPool'}
            steps{
                script{
                    copyRPM 'Latest','11.4'
                    setUpML '$WORKSPACE/xdmp/src/Mark*.rpm'
                    sh label:'deploy project', script: '''#!/bin/bash
                        export JAVA_HOME=$JAVA_HOME_DIR
                        export GRADLE_USER_HOME=$WORKSPACE/$GRADLE_DIR
                        export PATH=$GRADLE_USER_HOME:$JAVA_HOME/bin:$PATH
                        cd marklogic-python-client/test-app
                        ./gradlew -i mlDeploy -PmlPassword=admin
                    '''
                    sh label:'Run tests', script: '''#!/bin/bash
                        cd marklogic-python-client
                        python -m venv .venv;
                        source .venv/bin/activate;
                        pip install poetry;
                        poetry install;
                        pytest --junitxml=TestReport.xml || true
                    '''
                    junit 'marklogic-python-client/TestReport.xml'
                }
            }
        }
    }
}