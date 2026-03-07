#!/usr/bin/env bash
# Start the LaRa Dashboard Backend
set -e

# Change to the script's directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env..."
  export $(grep -v '^#' .env | xargs)
fi

# Homebrew's 'mvn' script hard-codes JDK 24 if JAVA_HOME is not set.
# This causes the "TypeTag :: UNKNOWN" error with Lombok.
# We dynamically fetch the path to the current system 'java' (which is JDK 21).
export JAVA_HOME=$(java -XshowSettings:properties -version 2>&1 | grep "java.home" | awk '{print $3}')

echo "Using JAVA_HOME: $JAVA_HOME"
echo "Starting Spring Boot..."

# Run the app
mvn clean spring-boot:run
