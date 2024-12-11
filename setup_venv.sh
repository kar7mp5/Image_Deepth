#! /bin/bash

# Set default values
PYTHON_VERSION="python3"  # Default Python version
REQUIREMENTS_FILE="requirements.txt"  # Default path to requirements file

# Process command line arguments
while getopts "p:r:" opt; do
    case $opt in
        p) PYTHON_VERSION="$OPTARG" ;;  # Specify Python version
        r) REQUIREMENTS_FILE="$OPTARG" ;;  # Specify requirements file path
        *)
        echo "Usage: $0 [-p python_version] [-r requirements_file]"
        exit 1
        ;;
    esac
done

# Create virtual environment
if [[ ! -d venv ]]; then
    echo "Creating Python virtual environment with $PYTHON_VERSION"
    sudo apt update
    sudo apt install -y python3-pip python3-venv

    # Create virtual environment with the specified Python version
    $PYTHON_VERSION -m venv venv || { echo "Failed to create virtual environment with $PYTHON_VERSION"; exit 1; }
else
    echo "Skipping virtual environment creation; 'venv' already exists."
fi

# Activate the virtual environment
source ./venv/bin/activate || { echo "Failed to activate virtual environment."; exit 1; }

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
if [[ -f $REQUIREMENTS_FILE ]]; then
    pip install -r "$REQUIREMENTS_FILE" || { echo "Failed to install dependencies from $REQUIREMENTS_FILE"; exit 1; }
else
    echo "Failed to find $REQUIREMENTS_FILE"
fi
