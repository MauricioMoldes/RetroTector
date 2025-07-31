#!/bin/bash
set -e

CONFIG_FILE="/opt/RetroTector/ReTe1.0.1/Database/Config.txt"
WORKDIR="/opt/RetroTector/ReTe1.0.1/Workplace/"

# Replace the WorkingDirectory line
sed -i "s|^WorkingDirectory:.*|WorkingDirectory: ${WORKDIR}|" "$CONFIG_FILE"

# Run the Java commands
cd /opt/RetroTector/ReTe1.0.1
java -cp RetroTector101.jar retrotector.RetroTectorEngine SweepDNA quit
java -cp RetroTector101.jar retrotector.RetroTectorEngine SweepScripts quit

