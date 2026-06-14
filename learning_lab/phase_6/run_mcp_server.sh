#!/bin/bash
# Wrapper script to run NomNom MCP server with proper environment

# Activate virtual environment
source ~/venv_nomnom/bin/activate

# Set Python path to include NomNom-Backend
export PYTHONPATH="/Users/ionahu/sources/NomNom/NomNom-Backend:$PYTHONPATH"

# Run the server
exec python /Users/ionahu/sources/NomNom/learning_lab/phase_6/nomnom_mcp_server.py
