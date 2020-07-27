# jacoco-report-uploader

## Description

It will try to run `mvn jacoco:report` in the project, and upload jacoco report.

## How to use it

```yml
#  Example that togeher with git clone, maven-test plugin

envs:
  FLOWCI_GIT_URL: "https://github.com/FlowCI/spring-petclinic-sample.git"
  FLOWCI_GIT_BRANCH: "master"
  FLOWCI_GIT_REPO: "spring-petclinic"

docker:
  image: "maven:3.6-jdk-8"

steps:
  - name: clone
    plugin: 'gitclone'
    allow_failure: false

  - name: run unit test
    envs:
      MVN_CMD: "mvn clean test"
    plugin: 'maven-runner'

  - name: upload jacoco report
    plugin: 'jacoco-report-uploader'
```
