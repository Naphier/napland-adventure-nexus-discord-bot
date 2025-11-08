#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_requirements() {
    if [ -f "${ROOT_DIR}/requirements.txt" ]; then
        echo "${ROOT_DIR}/requirements.txt"
    elif [ -f "${ROOT_DIR}/app/requirements.txt" ]; then
        echo "${ROOT_DIR}/app/requirements.txt"
    else
        echo ""
    fi
}

REQ_FILE="$(find_requirements)"
if [ -z "${REQ_FILE}" ]; then
    echo "Could not find requirements.txt" >&2
    exit 1
fi

REQ_DIR="$(cd "$(dirname "${REQ_FILE}")" && pwd)"
VENV_PATH="${REQ_DIR}/.venv"

if [ ! -d "${VENV_PATH}" ]; then
    python3 -m venv "${VENV_PATH}"
fi

if [ -f "${VENV_PATH}/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source "${VENV_PATH}/Scripts/activate"
elif [ -f "${VENV_PATH}/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "${VENV_PATH}/bin/activate"
else
    echo "Unable to locate activate script in ${VENV_PATH}" >&2
    exit 1
fi

pip install -r "${REQ_FILE}"

DEV_REQ_FILE="${REQ_DIR}/requirements_dev.txt"
if [ ! -f "${DEV_REQ_FILE}" ]; then
    if [ -f "${ROOT_DIR}/requirements_dev.txt" ]; then
        DEV_REQ_FILE="${ROOT_DIR}/requirements_dev.txt"
    elif [ -f "${ROOT_DIR}/app/requirements_dev.txt" ]; then
        DEV_REQ_FILE="${ROOT_DIR}/app/requirements_dev.txt"
    else
        echo "Could not find requirements_dev.txt" >&2
        exit 1
    fi
fi

pip install -r "${DEV_REQ_FILE}"
