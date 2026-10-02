xml_content = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>local</value>
    </property>
</configuration>
"""
with open("/opt/hadoop/etc/hadoop/mapred-site.xml", "w") as f:
    f.write(xml_content)
print("Updated mapred-site.xml")
