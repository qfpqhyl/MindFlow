#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

CONDA_ENV_NAME="${CONDA_ENV_NAME:-hack}"

mkdir -p "${LOG_DIR}"

activate_conda_env() {
  if ! command -v conda >/dev/null 2>&1; then
    echo "Warning: conda not found, continue with current shell environment."
    return
  fi

  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "${CONDA_ENV_NAME}"
}

is_pid_running() {
  local pid_file="$1"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}")"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

activate_conda_env

if is_pid_running "${BACKEND_PID_FILE}"; then
  echo "Backend is already running (PID: $(cat "${BACKEND_PID_FILE}"))."
else
  (
    cd "${ROOT_DIR}/backend"
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload >"${BACKEND_LOG}" 2>&1 &
    echo $! >"${BACKEND_PID_FILE}"
  )
  echo "Backend started. PID: $(cat "${BACKEND_PID_FILE}")"
fi

if is_pid_running "${FRONTEND_PID_FILE}"; then
  echo "Frontend is already running (PID: $(cat "${FRONTEND_PID_FILE}"))."
else
  (
    cd "${ROOT_DIR}/frontend"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 >"${FRONTEND_LOG}" 2>&1 &
    echo $! >"${FRONTEND_PID_FILE}"
  )
  echo "Frontend started. PID: $(cat "${FRONTEND_PID_FILE}")"
fi

echo "Backend log: ${BACKEND_LOG}"
echo "Frontend log: ${FRONTEND_LOG}"
