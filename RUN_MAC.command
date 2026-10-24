#!/bin/bash
# AI Study Buddy launcher for macOS
set -e
cd "$(dirname "$0")"

pause_on_error() {
  code=$?
  if [ "$code" -ne 0 ]; then
    echo
    echo "Lauch failed。"
    if [ -r /dev/tty ]; then
      read -r -p "Press Enter to close this window..." </dev/tty || true
    fi
  fi
}
trap pause_on_error EXIT

echo "======================================="
echo "     AI Study Buddy — macOS Launcher"
echo "======================================="

PYTHON=""
for candidate in python3 python3.13 python3.12 python3.11 python3.14 python3.15; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; assert (3, 11) <= sys.version_info[:2] < (3, 16)' >/dev/null 2>&1; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "can not find Python 3.11–3.15。"
  echo "please install Python: https://www.python.org/downloads/macos/"
  exit 1
fi

echo "Use Python: $($PYTHON --version)"

if [ ! -x ".venv/bin/python" ]; then
  echo "First time start：create Python enviroment..."
  "$PYTHON" -m venv .venv
fi

echo "install/check enviroment（first time need internet conection）..."
".venv/bin/python" -m pip install -r requirements.txt

echo
 echo "starting AI Study Buddy..."
 echo "if the web page not open automatically，pls visit http://localhost:8501"
 echo "lauch complete：return to this terminal window，use Control + C"
".venv/bin/python" -m streamlit run app.py
