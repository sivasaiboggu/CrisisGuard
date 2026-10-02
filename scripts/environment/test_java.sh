#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$PATH"

echo "=== Java 11 Environment Check ==="
echo "JAVA_HOME=$JAVA_HOME"
java -version

cat << 'EOF' > /tmp/JavaSmokeTest.java
public class JavaSmokeTest {
    public static void main(String[] args) {
        System.out.println("CrisisGuard Java 11 Smoke Test");
        System.out.println("Author: B.SIVASAI (2023BCS0228)");
        System.out.println("JVM Specification Version: " + System.getProperty("java.specification.version"));
        System.out.println("JVM Runtime Version: " + System.getProperty("java.version"));
        System.out.println("JVM Vendor: " + System.getProperty("java.vendor"));
    }
}
EOF

javac /tmp/JavaSmokeTest.java
java -cp /tmp JavaSmokeTest
rm -f /tmp/JavaSmokeTest.java /tmp/JavaSmokeTest.class
echo "Java 11 Smoke Test: PASS"
