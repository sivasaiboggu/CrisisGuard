import subprocess
import os

env = os.environ.copy()
env["HADOOP_HOME"] = "/opt/hadoop"
env["HIVE_HOME"] = "/opt/hive"
env["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
env["PATH"] = f"/usr/lib/jvm/java-8-openjdk-amd64/bin:/opt/hive/bin:/opt/hadoop/bin:{env.get('PATH', '')}"

query = "INSERT INTO default.crisisguard_smoke VALUES (1, 'B.SIVASAI', '2023BCS0228', 'OPERATIONAL');"
cmd = ["/opt/hive/bin/hive", "--hiveconf", "hive.root.logger=INFO,console", "-e", query]

res = subprocess.run(cmd, env=env, text=True, capture_output=True, cwd="/var/crisisguard/hive")
with open("/var/crisisguard/hive_run.log", "w") as f:
    f.write("=== STDOUT ===\n" + res.stdout + "\n=== STDERR ===\n" + res.stderr)
print("WROTE LOG, EXIT CODE:", res.returncode)
