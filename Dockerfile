FROM tomcat:9-jre8-alpine
COPY ./webvowl_1.1.7.war /usr/local/tomcat/webapps/webvowl.war