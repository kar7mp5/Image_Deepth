#! /bin/bash

if [[ ! -d venv ]]; then
    echo "Create python virtual environment"
    sudo apt update
    sudo apt install -y python3-pip python3-venv
    sudo apt install python3-pip
    python3 -m venv venv
else
    echo "Skip for creating virtual environment"
fi

source ./venv/bin/activate

pip install --upgrade pip

if [[ -f requirements.txt ]]; then
    pip3 install -r requirements.txt
else
    echo "Fail to find requirements.txt"
fi
