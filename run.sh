#!/bin/bash
# 启动 OWASP Top 10 课堂控制台
set -e
cd "$(dirname "$0")"
source /Users/tywin/ai-lab/.venv/bin/activate
echo "[run] cwd=$(pwd)"
echo "[run] python=$(which python)"
echo "[run] http://127.0.0.1:7861/"
exec python server.py
