#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Load environment variables safely
if [ -f .env ]; then
  echo "Loading environment variables from .env..."
  set -o allexport
  source .env
  set +o allexport
fi

# Ensure Maven is installed
if ! command -v mvn &> /dev/null; then
  echo "Error: Maven (mvn) is not installed."
  exit 1
fi

# Set JAVA_HOME (prefer macOS utility if available)
if command -v /usr/libexec/java_home &> /dev/null; then
  export JAVA_HOME=$(/usr/libexec/java_home -v 21)
else
  export JAVA_HOME=$(java -XshowSettings:properties -version 2>&1 | awk -F'= ' '/java.home/ {print $2}')
fi

echo "Using JAVA_HOME: $JAVA_HOME"
echo "Starting Spring Boot..."

# Run app (prefer wrapper if available)
if [ -f "./mvnw" ]; then
  ./mvnw clean spring-boot:run
else
  mvn clean spring-boot:run
fi