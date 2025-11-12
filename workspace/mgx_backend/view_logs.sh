#!/bin/bash
# 查看后端日志的便捷脚本

LOG_FILE="/Users/jianzhixu/Desktop/mgx/metadev/workspace/mgx_backend/api.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  日志文件不存在: $LOG_FILE"
    echo ""
    echo "请先启动后端并将日志输出到文件:"
    echo "  cd /Users/jianzhixu/Desktop/mgx/metadev/workspace"
    echo "  export \$(cat mgx_backend/.env | grep -v '^#' | xargs)"
    echo "  PYTHONPATH=/Users/jianzhixu/Desktop/mgx/metadev/workspace:\$PYTHONPATH python3 -m uvicorn mgx_backend.api:app --host 0.0.0.0 --port 8000 > mgx_backend/api.log 2>&1 &"
    exit 1
fi

echo "📋 查看后端日志 (按 Ctrl+C 退出)"
echo "日志文件: $LOG_FILE"
echo ""
tail -f "$LOG_FILE"
