#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export SCALA_HOME="/opt/scala"
export PATH="$SCALA_HOME/bin:$JAVA_HOME/bin:$PATH"

echo "=== Scala Verification ==="
scala -version

echo "=== Scala Expression Execution ==="
scala -e '
println("============================================================")
println("CrisisGuard Scala Smoke Test")
println("Author: B.SIVASAI")
println("Roll Number: 2023BCS0228")
println("Scala Version: " + util.Properties.versionString)
println("Java Runtime: " + System.getProperty("java.version"))
println("============================================================")
'

echo "Scala Smoke Test: PASS"
