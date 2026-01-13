#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating instance directory..."
mkdir -p instance

echo "Creating database tables..."
python create_db.py

echo "Build completed successfully!"
