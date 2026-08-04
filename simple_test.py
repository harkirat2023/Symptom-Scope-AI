# Simple test without importing complex modules
import asyncio
import os
import sys

# Set up path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Base directory: {base_dir}")
print(f"Files in backend/api/v1/: {os.listdir(os.path.join(base_dir, 'backend/api/v1'))}")
