#!/usr/bin/env bash
echo -e "\t\t\nLet's get you set up with..."
echo """
 ____       _      ___  ____ _____
| __ ) _ __(_)___ / _ \|  _ \_   _|
|  _ \| '__| / __| | | | |_) || |
| |_) | |  | \__ \ |_| |  __/ | |
|____/|_|  |_|___/\___/|_|    |_|
"""

echo "Checking requirements..."
# Checking node v18 installed
NODE_VERSION=$(node -v 2>/dev/null)
if [ -z "$NODE_VERSION" ]; then
    echo "Node.js is not installed."
    exit 1
fi
# Check if the node version is v18
if [[ $NODE_VERSION == v18.* ]]; then
    echo "Node.js version 18 is installed."
else
    echo "Node.js version 18 is NOT installed. Current version: $NODE_VERSION"
    echo "BrisOPT requires Node.js V18. Please install it here: https://nodejs.org/en and try again."
    exit 2
fi

# change to frtonend directory and run next in prod mode
cd frontend
echo "Installing frontend dependencies..."
npm install
echo "Building frontend..."
npm run build
npm run start -p 3000