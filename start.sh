#!/bin/bash
echo "Installing dependencies..."

# In AI Studio, ensure pip is available
if ! command -v pip3 &> /dev/null
then
    echo "pip3 not found, installing..."
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-venv python3.10-venv
fi

# Ensure virtualenv exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start the bot
echo "Starting bot..."
python3 bot.py
