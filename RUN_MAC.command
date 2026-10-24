#!/bin/bash
# AI Study Buddy launcher for macOS
set -e
cd "$(dirname "$0")"

pause_on_error() {
  code=$?
  if [ "$code" -ne 0 ]; then
    echo
    echo "启动未成功。请将上面的错误信息截图发给 ChatGPT。"
    if [ -r /dev/tty ]; then
      read -r -p "按 Enter 关闭这个窗口..." </dev/tty || true
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
  echo "没有找到 Python 3.11–3.15。"
  echo "请先安装 Python: https://www.python.org/downloads/macos/"
  exit 1
fi

echo "使用 Python: $($PYTHON --version)"

if [ ! -x ".venv/bin/python" ]; then
  echo "首次启动：创建独立 Python 环境..."
  "$PYTHON" -m venv .venv
fi

echo "安装/检查应用依赖（首次运行需要联网）..."
".venv/bin/python" -m pip install -r requirements.txt

echo
 echo "正在启动 AI Study Buddy..."
 echo "如果浏览器没有自动弹出，请访问 http://localhost:8501"
 echo "结束运行：返回此终端窗口，按 Control + C"
".venv/bin/python" -m streamlit run app.py
