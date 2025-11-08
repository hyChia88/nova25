#!/usr/bin/env python3
"""
CheatSheet Application Entry Point
Starts the Flask web server with integrated MCP agent
"""
import sys
import os

# Add python modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python', 'agent', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python', 'mcp_cheatsheet', 'src'))

from agent import run_server

if __name__ == '__main__':
    print("=" * 60)
    print("CheatSheet - Intelligent Learning Assistant")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the application at: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    run_server()

