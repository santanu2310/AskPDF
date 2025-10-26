#!/bin/bash

# --- Tmux Session Setup Script for Dev Environment ---

# Define the name for your new tmux session
SESSION_NAME="askpdf_dev"

PROJECT_ROOT="$HOME/Projects/askpdf"
EDITOR_VENV='source server/.venv/bin/activate'
SERVICE_VENV='source .venv/bin/activate'

# Check if the session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  echo "Creating new tmux session: $SESSION_NAME with four windows..."

  tmux new-session -d -s $SESSION_NAME -n "Editor" -c "$PROJECT_ROOT"
  tmux new-window -t $SESSION_NAME: -n "Server" -c "$PROJECT_ROOT"
  tmux new-window -t $SESSION_NAME: -n "Worker" -c "$PROJECT_ROOT"
  tmux new-window -t $SESSION_NAME: -n "Assistant" -c "$PROJECT_ROOT"

  # Editor: Activate Venv and open Neovim/Vim in the current directory
  tmux send-keys -t $SESSION_NAME:Editor "$EDITOR_VENV" C-m
  tmux send-keys -t $SESSION_NAME:Editor 'nvim .' C-m

  # === Server Window Setup (Split into Server and Client Panes) ===
  tmux send-keys -t $SESSION_NAME:Server "cd server" C-m
  tmux send-keys -t $SESSION_NAME:Server "$SERVICE_VENV" C-m
  tmux send-keys -t $SESSION_NAME:Server 'fastapi dev app/main.py' C-m

  tmux split-window -t $SESSION_NAME:Server -v -c "$PROJECT_ROOT"

  tmux send-keys -t $SESSION_NAME:Server "cd client" C-m
  tmux send-keys -t $SESSION_NAME:Server 'bun run dev' C-m
  # === End Server Window Setup ===

  # Worker: Activate Venv and run the background worker process
  tmux send-keys -t $SESSION_NAME:Worker "cd pdf_processor" C-m
  tmux send-keys -t $SESSION_NAME:Worker "$SERVICE_VENV" C-m
  tmux send-keys -t $SESSION_NAME:Worker 'celery -A app.celery_app worker -l info -c 1' C-m

  # Assistant: Activate Venv and run an auxiliary script/monitor
  tmux send-keys -t $SESSION_NAME:Assistant 'gemini' C-m

else
  echo "Session '$SESSION_NAME' already exists. Attaching..."
fi

# Attach to the session, whether it was new or existing
tmux attach-session -t $SESSION_NAME
