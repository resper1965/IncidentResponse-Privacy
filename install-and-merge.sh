#!/bin/bash

# Install asyncpg and run database merge on VPS
echo "Installing asyncpg and running database merge..."

cd /opt/privacy

# Activate virtual environment and install asyncpg
source venv/bin/activate
pip install asyncpg --quiet
deactivate

# Run the database merge
python3 vps-database-merge.py

echo "Database merge completed"