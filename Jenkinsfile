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
                pytest --junitxml=TestReport.xml
              '''
            }
            post{
              always{
                junit testResults: 'marklogic-python-client/TestReport.xml', allowEmptyResults: true
                updateWorkspacePermissions()
                sh label:'mlcleanup', script: '''#!/bin/bash
                  cd marklogic-python-client/test-app
                  docker-compose down -v || true
                '''
                cleanupDocker()
              }
            }
        }
        stage('publish'){
            agent {label 'devExpLinuxPool'}
            when {
                branch 'develop'
            }
            steps{
                sh label:'build-distributions', script: '''#!/bin/bash
                  set -e
                  export PATH="${PYTHON313_BIN}:${PATH}"
                  cd marklogic-python-client
                  rm -f dist/marklogic_python_client-*.whl dist/marklogic_python_client-*.tar.gz
                  python3.13 -m pip install poetry
                  poetry build
                '''
                archiveArtifacts artifacts: 'marklogic-python-client/dist/marklogic_python_client-*.whl, marklogic-python-client/dist/marklogic_python_client-*.tar.gz', fingerprint: true, followSymlinks: false
                script {
                  def artifactory = Artifactory.newServer(url: 'https://bed-artifactory.bedford.progress.com:443/artifactory/', credentialsId: 'builder-credentials-artifactory')
                  def uploadSpec = """{
                    "files": [
                      {
                        "pattern": "${WORKSPACE}/marklogic-python-client/dist/marklogic_python_client-*.whl",
                        "target": "ml-generic-dev-tierpoint/marklogic-python-client/",
                        "props": "build.number=${BUILD_NUMBER};build.name=${JOB_NAME}"
                      },
                      {
                        "pattern": "${WORKSPACE}/marklogic-python-client/dist/marklogic_python_client-*.tar.gz",
                        "target": "ml-generic-dev-tierpoint/marklogic-python-client/",
                        "props": "build.number=${BUILD_NUMBER};build.name=${JOB_NAME}"
                      }
                    ]
                  }"""
                  artifactory.upload(uploadSpec)
                  echo "${uploadSpec}"
                }
            }
            post{
                always{
                    updateWorkspacePermissions()
                }
            }
        }
    }
}
