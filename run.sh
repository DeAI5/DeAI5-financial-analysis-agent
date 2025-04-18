#!/bin/bash
echo "Starting Financial Analysis Agent Application..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
elif [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Check if required deps are installed
if ! command -v python &> /dev/null; then
  echo "Error: Python is not installed"
  exit 1
fi

if ! command -v npm &> /dev/null; then
  echo "Error: npm is not installed"
  exit 1
fi

# Start the backend
echo "Starting Python Flask backend..."
cd backend && python app.py &
BACKEND_PID=$!

# Wait a moment for the backend to initialize
sleep 2

# Start the frontend
echo "Starting Next.js frontend..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo "Services started!"
echo "Financial Analysis Agent is running at: http://localhost:3000"
echo "Press Ctrl+C to stop all services"

# Handle termination
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait