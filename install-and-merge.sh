#!/bin/bash

# Install asyncpg and run database merge on VPS
echo "Installing asyncpg and running database merge..."

cd /opt/privacy

# Install asyncpg directly in virtual environment
/opt/privacy/venv/bin/pip install asyncpg

# Run the database merge using virtual environment python
/opt/privacy/venv/bin/python3 vps-database-merge.py

echo "Database merge completed"