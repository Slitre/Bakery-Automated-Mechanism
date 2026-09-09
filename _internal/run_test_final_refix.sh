#!/bin/bash

# Path to the Python interpreter
PYTHON_PATH=$(which python3)  # or $(which python) depending on your system

# Path to the Python script
SCRIPT_PATH="$1"
ASSIGNMENT_FILE="$2"

# Print paths for debugging
echo "Python Path: $PYTHON_PATH"
echo "Script Path: $SCRIPT_PATH"
echo "Assignment File: $ASSIGNMENT_FILE"

# Verify script existence
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if Python path exists
if [ ! -x "$PYTHON_PATH" ]; then
    echo "Error: Python executable not found at $PYTHON_PATH"
    exit 1
fi

# Execute the script
"$PYTHON_PATH" "$SCRIPT_PATH" "$ASSIGNMENT_FILE"
