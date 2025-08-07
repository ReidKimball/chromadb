# This script automates the process of running the backend and frontend servers.

# Define paths
$backendPath = ".\backend"
$frontendPath = ".\frontend"

# Start Backend Server
Write-Host "Starting backend server in a new window..."
$backendCommand = "cd $backendPath; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Start Frontend Server
Write-Host "Starting frontend server in a new window..."
$frontendCommand = "cd $frontendPath; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Application startup initiated. Please see the new terminal windows for server status."
