#!/bin/bash

set -e

INPUT_FASTA="$1"
OUTPUT_DIR="$2"
shift 2

if [[ -z "$INPUT_FASTA" || -z "$OUTPUT_DIR" ]]; then
    echo "Usage: run_retro.sh <input.fasta> <output_dir> [RetroTector options]"
    echo "Example options: -l 200 -i 90 -d 15000"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Running RetroTector on $INPUT_FASTA with output to $OUTPUT_DIR"
echo "Additional options: $@"

java -jar /opt/RetroTector/dist/rtt.jar "$INPUT_FASTA" "$OUTPUT_DIR" "$@"
