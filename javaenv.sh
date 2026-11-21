#!/bin/sh

# Use the in-tree JDK 11; /usr/lib/jvm/java-8-openjdk-amd64 does not exist
# on this host.
export JAVA_HOME=$(cd "$(dirname "$0")" && pwd)/prebuilts/jdk/jdk11/linux-x86
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar

export PATH=$(cd "$(dirname "$0")" && pwd)/tools/x7pro-host:$JAVA_HOME/bin:$PATH
