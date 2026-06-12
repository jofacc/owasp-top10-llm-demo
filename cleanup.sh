#!/bin/bash
# 课前/课后清理：日志 + 桌面 PWNED 文件
set -e
cd "$(dirname "$0")"
echo "[cleanup] truncate logs"
> logs/agent.log 2>/dev/null || true
> logs/exec.log  2>/dev/null || true
> logs/rce.log   2>/dev/null || true
> logs/guard.log 2>/dev/null || true
echo "[cleanup] remove desktop PWNED files"
rm -f ~/Desktop/PWNED_*.txt 2>/dev/null || true
ls -la logs/ 2>/dev/null || true
echo "[cleanup] done"
