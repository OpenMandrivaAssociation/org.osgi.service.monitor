Name:		org.osgi.service.monitor
Version:	1.0.0
Release:	1
Summary:	OSGi Monitor Admin API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.monitor/%{version}/org.osgi.service.monitor-%{version}-sources.jar

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Monitor Admin 1.0. Status variables and monitoring jobs. The
package version is 1.0. There are no framework types. This build
targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
mkdir -p src/main/java src/main/resources
python - <<'PY'
import shutil
from pathlib import Path

src = Path("org/osgi/service/monitor")
java_root = Path("src/main/java/org/osgi/service/monitor")
res = Path("src/main/resources/org/osgi/service/monitor")
java_root.mkdir(parents=True)
res.mkdir(parents=True)
info = (src / "packageinfo").read_bytes()
if info != b"version 1.0\n":
    raise SystemExit("packageinfo " + repr(info))
(res / "packageinfo").write_bytes(info)
(src / "packageinfo").unlink()
for path in sorted(src.glob("*.java")):
    shutil.move(path, java_root / path.name)
shutil.rmtree("org")
names = sorted(path.name for path in java_root.glob("*.java"))
expect = [
    "MonitorAdmin.java",
    "MonitorListener.java",
    "MonitorPermission.java",
    "Monitorable.java",
    "MonitoringJob.java",
    "StatusVariable.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if not Path("about.html").is_file():
    raise SystemExit("missing about.html")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.monitor</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.monitor</name>
  <description>OSGi Monitor Admin.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.monitor</artifactId>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<dependencies>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.monitor-%{version}.jar --describe-module org.osgi.service.monitor > module-describe.txt
grep -q '^org.osgi.service.monitor' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.monitor-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    info = zf.read("org/osgi/service/monitor/packageinfo")
if info != b"version 1.0\n":
    raise SystemExit("jar packageinfo " + repr(info))
PY

%files -f .mfiles
%doc LICENSE about.html
