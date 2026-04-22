import os
import sys
import subprocess

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

python_exe = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
command = [python_exe, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000']
print(f"Working dir: {os.getcwd()}")
print(f"Command: {' '.join(command)}")
sys.exit(subprocess.call(command))
